"""Aqara WS-USC03 smart wall switch quirk for ZHA."""

import logging
import time
import copy

from zigpy.profiles import zha
from zigpy.quirks import CustomEndpoint
from zigpy.quirks.v2 import QuirkBuilder, CustomDeviceV2
from zigpy.types import t, LVBytes
from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement
from zigpy.zcl.clusters.general import (
    AnalogInput,
    Basic, 
    Groups,
    Identify, 
    MultistateInput, 
    OnOff,
    PowerConfiguration, 
)

from zhaquirks import (
    CustomCluster,
    EventableCluster,
    LocalDataCluster,
)
from zhaquirks.const import (
    ATTRIBUTE_ID,
    ATTRIBUTE_NAME,
    ARGS,
    CLUSTER_ID,
    COMMAND,
    COMMAND_BUTTON_DOUBLE,
    COMMAND_BUTTON_SINGLE,
    DEVICE_TYPE,
    ENDPOINT_ID,
    INPUT_CLUSTERS,
    OUTPUT_CLUSTERS,
    PRESS_TYPE,
    PROFILE_ID,
    VALUE,
    ZHA_SEND_EVENT,
)
from zhaquirks.xiaomi import XiaomiCluster, ElectricalMeasurementCluster
from zhaquirks.xiaomi.aqara.opple_remote import MultistateInputCluster

_LOGGER = logging.getLogger(__name__)

# Lumi/Aqara uses 0xFCC0 as their manufacturer specific cluster ID
LUMI_CLUSTER_ID = 0xFCC0

# Operation mode constants
#OPMODE_DECOUPLED = 0x00
#OPMODE_CONTROL_RELAY = 0x01

STATUS_TYPE_ATTR = 0x0055

class AqaraB1naus01Device(CustomDeviceV2):
    """Custom device class to add endpoint 41."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define endpoint 41 replacement data
        ep41_replacement = {
            PROFILE_ID: zha.PROFILE_ID,
            DEVICE_TYPE: zha.DeviceType.ON_OFF_SWITCH,
            INPUT_CLUSTERS: [
                MultistateInputCluster,
            ],
            OUTPUT_CLUSTERS: [],
        }
        
        # Add endpoint 41
        self._add_endpoint(41, ep41_replacement)
    
    def _add_endpoint(self, endpoint_id, replacement_data):
        """Helper method to add a new endpoint."""
        self.endpoints[endpoint_id] = CustomEndpoint(
            self,
            endpoint_id,
            replacement_data,
            self,
        )


#class AnalogInputCluster(CustomCluster, AnalogInput):
#    """Analog input cluster, only used to relay power consumption information to ElectricalMeasurementCluster."""
#    
#class ElectricalMeasurementCluster(LocalDataCluster, ElectricalMeasurement):
#    """Electrical measurement cluster to receive reports that are sent to the basic cluster."""

class AqaraB1naus01OnOffCluster(OnOff):
    """Custom OnOff cluster."""

class AqaraB1naus01ManufCluster(EventableCluster, XiaomiCluster):
    """Aqara manufacturer specific cluster."""

    cluster_id = LUMI_CLUSTER_ID

    attributes = {
        **XiaomiCluster.attributes,
        0x0200: ('operation_mode', t.uint8_t, True),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._operation_mode = 0x01  # OPMODE_CONTROL_RELAY
        self._update_attribute(0x0200, self._operation_mode)

    def _update_attribute(self, attrid, value):
        _LOGGER.debug(
            "Manufacturer cluster attribute update - ID: 0x%04x, Value: %s",
            attrid, value
        )

        # Skip sending events for attribute_id 223, 229, and 247 (LVBytes parsing error)
        if attrid in (223, 229, 247):
            return

        super()._update_attribute(attrid, value)


class MultistateInputCluster(EventableCluster, CustomCluster, MultistateInput):
    """Multistate input cluster for button press detection."""

    PRESS_TYPES = {
        1: "single",
        2: "double",
    }
    
    def __init__(self, *args, **kwargs):
        """Init."""
        self._current_state = None
        super().__init__(*args, **kwargs)

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if attrid == STATUS_TYPE_ATTR:
            self._current_state = PRESS_TYPES.get(value)
            button = ENDPOINT_MAP.get(self.endpoint.endpoint_id)
            event_args = {
                BUTTON: button,
                PRESS_TYPE: self._current_state,
                ATTR_ID: attrid,
                VALUE: value,
            }
            action = f"{button}_{self._current_state}"
            self.listener_event(ZHA_SEND_EVENT, action, event_args)
            # show something in the sensor in HA
            super()._update_attribute(0, action)


(
    QuirkBuilder("LUMI", "lumi.switch.b1naus01")
    .device_class(AqaraB1naus01Device)
#    .adds(AnalogInputCluster, endpoint_id=1)
    .adds(AqaraB1naus01OnOffCluster, endpoint_id=1)
    .adds(AqaraB1naus01ManufCluster, endpoint_id=1)
#    .adds(MultistateInputCluster, endpoint_id=1)
#    .adds(ElectricalMeasurementCluster, endpoint_id=1)
    .switch(
        "operation_mode",
        LUMI_CLUSTER_ID,
        translation_key="operation_mode",
        force_inverted=True,
        fallback_name="Decoupled Mode"
    )
    .skip_configuration(skip_configuration=False)
    .device_automation_triggers({
        ("button", "single"): {
            ENDPOINT_ID: 41,
            CLUSTER_ID: 18,
            COMMAND: "attribute_updated",
            ARGS: {ATTRIBUTE_ID: 85, ATTRIBUTE_NAME: "present_value", VALUE: 1},
        },
        ("button", "double"): {
            ENDPOINT_ID: 41,
            CLUSTER_ID: 18,
            COMMAND: "attribute_updated",
            ARGS: {ATTRIBUTE_ID: 85, ATTRIBUTE_NAME: "present_value", VALUE: 2},
        },
    }) 
    .add_to_registry()
)
