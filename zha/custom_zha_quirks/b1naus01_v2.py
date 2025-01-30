"""Aqara WS-USC03 smart wall switch quirk for ZHA."""

from zigpy.profiles import zha
from zigpy.quirks import CustomEndpoint
from zigpy.quirks.v2 import QuirkBuilder, CustomDeviceV2
from zigpy.types import t, LVBytes
from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement
from zigpy.zcl.clusters.smartenergy import Metering
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
from zhaquirks.xiaomi import XiaomiCluster, ElectricalMeasurementCluster, MeteringCluster
from zhaquirks.xiaomi.aqara.opple_remote import MultistateInputCluster


# Lumi/Aqara uses 0xFCC0 as their manufacturer specific cluster ID
LUMI_CLUSTER_ID = 0xFCC0



class AqaraB1naus01Device(CustomDeviceV2):
    """Custom device class to add endpoint 21, 31, and 41."""
    
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

        # Define endpoint 21 replacement data
        ep21_replacement = {
            PROFILE_ID: zha.PROFILE_ID,
            DEVICE_TYPE: zha.DeviceType.ON_OFF_SWITCH,
            INPUT_CLUSTERS: [
                AnalogInputCluster,
            ],
            OUTPUT_CLUSTERS: [],
        }

        # Add endpoint 21
        self._add_endpoint(21, ep21_replacement)
    

    def _add_endpoint(self, endpoint_id, replacement_data):
        """Helper method to add a new endpoint."""
        self.endpoints[endpoint_id] = CustomEndpoint(
            self,
            endpoint_id,
            replacement_data,
            self,
        )


class AnalogInputCluster(CustomCluster, AnalogInput):
    """Analog input cluster, only used to relay power consumption information to ElectricalMeasurementCluster.

    The AnalogInput cluster responsible for reporting power consumption seems to be on endpoint 21 for newer devices
    and either on endpoint 1 or 2 for older devices.
    """

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if (
            attrid == self.AttributeDefs.present_value.id
            and value is not None
            and value >= 0
        ):
            # ElectricalMeasurementCluster is assumed to be on endpoint 1
            self.endpoint.device.endpoints[1].electrical_measurement.update_attribute(
                ElectricalMeasurement.AttributeDefs.active_power.id,
                round(value * 10),
            )


class ElectricalMeasurementCluster(LocalDataCluster, ElectricalMeasurement):
    """Electrical measurement cluster to receive reports that are sent to the basic cluster."""

    POWER_ID = ElectricalMeasurement.AttributeDefs.active_power.id
    VOLTAGE_ID = ElectricalMeasurement.AttributeDefs.rms_voltage.id
    CONSUMPTION_ID = ElectricalMeasurement.AttributeDefs.total_active_power.id

    _CONSTANT_ATTRIBUTES = {
        ElectricalMeasurement.AttributeDefs.power_multiplier.id: 1,
        ElectricalMeasurement.AttributeDefs.power_divisor.id: 1,
        ElectricalMeasurement.AttributeDefs.ac_power_multiplier.id: 1,
        ElectricalMeasurement.AttributeDefs.ac_power_divisor.id: 10,
    }

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        # put a default value so the sensors are created
        if self.POWER_ID not in self._attr_cache:
            self._update_attribute(self.POWER_ID, 0)
        if self.VOLTAGE_ID not in self._attr_cache:
            self._update_attribute(self.VOLTAGE_ID, 0)
        if self.CONSUMPTION_ID not in self._attr_cache:
            self._update_attribute(self.CONSUMPTION_ID, 0)

class AqaraB1naus01OnOffCluster(OnOff, CustomCluster):
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

        # Skip sending events for attribute_id 223, 229, and 247 (LVBytes parsing error)
        if attrid in (223, 229, 247):
            return

        super()._update_attribute(attrid, value)

class MeteringCluster(LocalDataCluster, Metering):
    """Metering cluster to receive reports that are sent to the basic cluster."""

    CURRENT_SUMM_DELIVERED_ID = Metering.AttributeDefs.current_summ_delivered.id
    _CONSTANT_ATTRIBUTES = {
        Metering.AttributeDefs.unit_of_measure.id: 0, 
        Metering.AttributeDefs.multiplier.id: 1,
        Metering.AttributeDefs.divisor.id: 1000,
        Metering.AttributeDefs.summation_formatting.id: 0b0_0100_011,  
        Metering.AttributeDefs.metering_device_type.id: 0,  
    }

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        # put a default value so the sensor is created
        if self.CURRENT_SUMM_DELIVERED_ID not in self._attr_cache:
            self._update_attribute(self.CURRENT_SUMM_DELIVERED_ID, 0)


class MultistateInputCluster(EventableCluster, CustomCluster, MultistateInput):
    """Multistate input cluster for button press detection."""

(
    QuirkBuilder("LUMI", "lumi.switch.b1naus01")
    .device_class(AqaraB1naus01Device)
    .adds(AqaraB1naus01OnOffCluster, endpoint_id=1)
    .adds(AqaraB1naus01ManufCluster, endpoint_id=1)
    .adds(MeteringCluster, endpoint_id=1)
    .adds(ElectricalMeasurementCluster, endpoint_id=1)
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
