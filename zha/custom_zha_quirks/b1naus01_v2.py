"""Aqara WS-USC03 smart wall switch quirk for ZHA."""

import logging
from zigpy.profiles import zha
from zigpy.quirks import CustomEndpoint
from zigpy.quirks.v2 import QuirkBuilder, CustomDeviceV2
from zigpy.types import t, LVBytes
from zigpy.zcl.clusters.general import (
    MultistateInput, 
    OnOff,
    Basic, 
    PowerConfiguration, 
    Identify, 
    Groups
)

from zhaquirks import EventableCluster, CustomCluster
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


from zhaquirks.xiaomi import XiaomiAqaraE1Cluster
from zhaquirks.xiaomi.aqara.opple_remote import MultistateInputCluster


_LOGGER = logging.getLogger(__name__)

# Lumi/Aqara uses 0xFCC0 as their manufacturer specific cluster ID
LUMI_CLUSTER_ID = 0xFCC0

# Operation mode constants
OPMODE_DECOUPLED = 0x00
OPMODE_CONTROL_RELAY = 0x01


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
        

class AqaraB1naus01OnOffCluster(EventableCluster, OnOff):
    """Custom OnOff cluster."""

    def handle_cluster_request(self, tsn, command_id, args):
        """Handle incoming cluster requests."""
        _LOGGER.debug("OnOff cluster request - TSN: %s, Command: %s, Args: %s", tsn, command_id, args)
        super().handle_cluster_request(tsn, command_id, args)

    def _update_attribute(self, attrid, value):
        """Handle attribute updates."""
        _LOGGER.debug("OnOff attribute update - ID: 0x%04x, Value: %s", attrid, value)
        super()._update_attribute(attrid, value)
        
        # Get attribute name safely
        attribute_name = f"Unknown_{attrid:04x}"
        if attrid in self.attributes:
            attribute_def = self.attributes[attrid]
            attribute_name = attribute_def.name
        
        # Emit the event for attribute updates
        self.listener_event(
            ZHA_SEND_EVENT,
            "attribute_updated",
            {
                "attribute_id": attrid,
                "attribute_name": attribute_name,
                "value": value
            }
        )
        

class AqaraB1naus01ManufCluster(EventableCluster, XiaomiAqaraE1Cluster):
    """Aqara manufacturer specific cluster."""

    # Define cluster ID if not already defined
    cluster_id = LUMI_CLUSTER_ID

    # Define the attributes more explicitly
    attributes = {
        # Keep existing XiaomiAqaraE1Cluster attributes
        **XiaomiAqaraE1Cluster.attributes,
        # Add our custom attributes with proper ZCL definitions
        0x0200: ('operation_mode', t.uint8_t, True),  # Add True for read permission
        0x00FC: ('action_state', t.uint8_t, True),
        0x0112: ('decoupled_button', t.uint8_t, True),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._operation_mode = OPMODE_CONTROL_RELAY
        # Initialize the attribute value
        self._update_attribute(0x0200, self._operation_mode)

    def _handle_cluster_request(self, tsn, command_id, args):
        """Handle cluster specific commands."""
        _LOGGER.debug(
            "Manufacturer cluster request - TSN: %s, Command: %s, Args: %s",
            tsn, command_id, args
        )
        super()._handle_cluster_request(tsn, command_id, args)

    def _update_attribute(self, attrid, value):
        """Handle attribute updates."""
        _LOGGER.debug(
            "Manufacturer cluster attribute update - ID: 0x%04x, Value: %s",
            attrid, value
        )

        # Handle operation mode updates
        if attrid == 0x0200 and isinstance(value, int):
            self._operation_mode = value
            _LOGGER.debug("Operation mode updated to: %s", value)

        # Handle raw attribute data
        if attrid in (0x00F7, 0x00FF):
            try:
                if isinstance(value, (bytes, t.LVBytes)):
                    # Try to parse the data for button events
                    data = bytes(value)
                    _LOGGER.debug("Raw data received: %s", data.hex())
                    
                    # Look for button press patterns in the data
                    if len(data) > 2:
                        # Check for button press indicators
                        for i in range(len(data)-1):
                            if data[i] in (0x01, 0x02, 0x03) and data[i+1] in (0x01, 0x02):
                                press_type = "single" if data[i+1] == 0x01 else "double"
                                _LOGGER.debug("Detected button press: %s", press_type)
                                self.listener_event(
                                    ZHA_SEND_EVENT,
                                    "button_press",
                                    {
                                        "press_type": press_type,
                                        "value": data[i+1]
                                    }
                                )
                return  # Skip normal attribute processing for raw data
            except Exception as e:
                _LOGGER.debug("Error processing raw data: %s", e)
                return

        try:
            super()._update_attribute(attrid, value)
            
            # Emit event for all other attribute updates
            if attrid not in (0x00F7, 0x00FF):
                # Get attribute name safely
                attribute_name = f"Unknown_{attrid:04x}"
                if attrid in self.attributes:
                    attribute_def = self.attributes[attrid]
                    attribute_name = attribute_def[0] if isinstance(attribute_def, tuple) else attribute_def.name
                
                self.listener_event(
                    ZHA_SEND_EVENT,
                    "attribute_updated",
                    {
                        "attribute_id": attrid,
                        "attribute_name": attribute_name,
                        "value": value
                    }
                )
        except Exception as e:
            _LOGGER.debug("Error in attribute update: %s", e)
            

class MultistateInputCluster(EventableCluster, CustomCluster, MultistateInput):
    """Multistate input cluster for button press detection."""
    
    PRESS_TYPES = {
        1: "single",
        2: "double",
    }

    def __init__(self, *args, **kwargs):
        """Initialize the cluster."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.button_press_cluster = self

    def _update_attribute(self, attrid, value):
        """Handle attribute updates from the device."""
        super()._update_attribute(attrid, value)

        if attrid == 0x0055:  # present_value attribute
            try:
                press_type = self.PRESS_TYPES.get(value)
                if press_type:
                    self.endpoint.device.button_press_cluster = self
                    
                    # Get attribute name safely
                    attribute_name = "present_value"
                    if attrid in self.attributes:
                        attribute_def = self.attributes[attrid]
                        attribute_name = attribute_def.name
                    
                    event_args = {
                        "attribute_id": attrid,
                        "attribute_name": attribute_name,
                        "value": value
                    }
                    
                    _LOGGER.debug(
                        "[%s:%s] Button press detected: %s",
                        self.endpoint.device.nwk,
                        self.endpoint.endpoint_id,
                        press_type
                    )
                    
                    self.listener_event(
                        ZHA_SEND_EVENT,
                        "attribute_updated",
                        event_args
                    )
            except Exception as e:
                _LOGGER.debug("Error processing button press: %s", e)
                
                
(
    QuirkBuilder("LUMI", "lumi.switch.b1naus01")
    .device_class(AqaraB1naus01Device)
    .adds(AqaraB1naus01OnOffCluster, endpoint_id=1)
    .adds(AqaraB1naus01ManufCluster, endpoint_id=1)
    .adds(MultistateInputCluster, endpoint_id=1)
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
