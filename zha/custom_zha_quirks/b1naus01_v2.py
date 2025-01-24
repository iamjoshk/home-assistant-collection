"""Xiaomi aqara single rocker switch devices."""

import copy
import json
import base64

from enum import Enum
#from datetime import datetime
#from typing import Any

from zigpy.types import t, LVBytes

from zigpy.quirks.v2 import QuirkBuilder, CustomDeviceV2
from zigpy.quirks.v2.homeassistant import PERCENTAGE, EntityType, EntityPlatform
from zigpy.quirks.v2.homeassistant.sensor import SensorDeviceClass, SensorStateClass
from zigpy.zcl.clusters.general import (
    Alarms,
    AnalogInput,
    Basic,
    DeviceTemperature,
    GreenPowerProxy,
    Groups,
    Identify,
    MultistateInput,
    OnOff,
    Ota,
    Scenes,
    Time,
)

from zigpy.quirks import CustomCluster

from homeassistant.const import ATTR_DEVICE_ID

from zhaquirks import Bus, EventableCluster
from zhaquirks.const import (
    ARGS,
    ATTR_ID,
    ATTRIBUTE_ID,
    ATTRIBUTE_NAME,
    BUTTON,
    BUTTON_1,
    BUTTON_2,
    CLUSTER_ID,
    COMMAND,
    COMMAND_ATTRIBUTE_UPDATED,
    DEVICE_TYPE,
    DOUBLE_PRESS,
    ENDPOINT_ID,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PRESS_TYPE,
    PROFILE_ID,
    SHORT_PRESS,
    SKIP_CONFIGURATION,
    VALUE,
    ZHA_SEND_EVENT
)
from zhaquirks.xiaomi import (
    LUMI,
    XIAOMI_NODE_DESC,
    AnalogInputCluster,
    BasicCluster,
    DeviceTemperatureCluster,
    ElectricalMeasurementCluster,
    MeteringCluster,
    OnOffCluster,
    XiaomiCustomDevice,
    XiaomiCluster,
    XiaomiPowerConfiguration,
    XiaomiQuickInitDevice,    
    
)

from zhaquirks.xiaomi.aqara.opple_remote import MultistateInputCluster, OppleCluster


#XIAOMI_COMMAND_SINGLE = "41_single"
#XIAOMI_COMMAND_DOUBLE = "41_double"
#XIAOMI_COMMAND_HOLD = "1_hold"
#ATTRIBUTE_ON_OFF = "on_off"
#DOUBLE = "double"
#HOLD = "long press"
#PRESS_TYPES = {0: "long press", 1: "single", 2: "double"}
#SINGLE = "single"
#STATUS_TYPE_ATTR = 0x0055  # decimal = 85
#XIAOMI_CLUSTER_ID = 0xFFFF
#XIAOMI_DEVICE_TYPE = 0x5F01
#XIAOMI_DEVICE_TYPE2 = 0x5F02
#XIAOMI_DEVICE_TYPE3 = 0x5F03

PRESS_TYPES = {0: "hold", 1: "single", 2: "double", 3: "triple", 255: "release"}

class OppleOperationMode(t.uint8_t, Enum):
    """Opple operation_mode enum."""
    Decoupled = 0x00
    Coupled = 0x01

class WallSwitchOnOffCluster(OnOff, EventableCluster):
    """WallSwitchOnOffCluster: fire events corresponding to press type."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint.device.wall_switch_cluster = self

    def handle_cluster_request(self, tsn, command_id, args):
        """Handle incoming OnOff commands and emit zha_event."""
        print(f"handle_cluster_request called with command_id: {command_id}, args: {args}")
        press_type = None

        if command_id == 0x00:  # On command
            press_type = "single_press"
        elif command_id == 0x01:  # Off command
            press_type = "double_press"
        elif command_id == 0x02:  # Toggle command
            press_type = "long_press"

        if press_type:
            print(f"Emitting button event: {press_type}")
            self._emit_button_event(press_type)

    def _emit_button_event(self, press_type):
        """Emit a zha_event with the button press details."""
        print(f"_emit_button_event called with press_type: {press_type}")
        self.listener_event(
            ZHA_SEND_EVENT,
            self._get_event_name(press_type),
            {
                "unique_id": str(self.endpoint.device.ieee),
                "endpoint_id": self.endpoint.endpoint_id,
                "cluster_id": self.cluster_id,
                "command": press_type,
                "args": {"press_type": press_type},
            },
        )

    def _get_event_name(self, press_type):
        """Generate a unique event name."""
        return f"{self.endpoint.device.ieee}_{press_type}"

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, t.LVBytes):
            return base64.b64encode(obj).decode('utf-8')
        return super().default(obj)

class OppleSwitchCluster(OppleCluster, EventableCluster):
    """Xiaomi mfg cluster implementation."""

    attributes = copy.deepcopy(OppleCluster.attributes)
    attributes.update(
        {
            0x0200: ("operation_mode", OppleOperationMode, True),
            0x00F7: ('aqara_attributes', t.LVBytes),  # 247 - Various device attributes
            0x00FF: ('manufacture_info', t.LVBytes),  # 255 - Device info
        }
    )

    def _update_attribute(self, attrid, value):
        print(f"_update_attribute called with attrid: {attrid}, value: {value}")
        if isinstance(value, t.LVBytes):
            encoded_value = base64.b64encode(value).decode('utf-8')
            super()._update_attribute(attrid, encoded_value)
            value = encoded_value
        else:
            super()._update_attribute(attrid, value)

        if attrid == 0x0200:  # operation_mode attribute
            self._handle_operation_mode_update(value)
        elif attrid == 0x00FC:
            self._current_state = PRESS_TYPES.get(value)
            event_args = {
                "button": self.endpoint.endpoint_id,
                "press_type": self._current_state,
                "attr_id": attrid,
                "value": value,
            }
            action = f"{self.endpoint.endpoint_id}_{self._current_state}"
            self.listener_event(ZHA_SEND_EVENT, action, event_args)
            super()._update_attribute(0, action)

    def _handle_operation_mode_update(self, value):
        """Handle operation mode updates and emit event if in decoupled mode."""
        print(f"_handle_operation_mode_update called with value: {value}")
        if value == OppleOperationMode.Decoupled:
            self._emit_decoupled_mode_event()

    def _emit_decoupled_mode_event(self):
        """Emit a zha_event indicating the device is in decoupled mode."""
        print("_emit_decoupled_mode_event called")
        self.listener_event(
            ZHA_SEND_EVENT,
            self._get_event_name("decoupled_mode"),
            {
                "unique_id": str(self.endpoint.device.ieee),
                "endpoint_id": self.endpoint.endpoint_id,
                "cluster_id": self.cluster_id,
                "command": "decoupled_mode",
                "args": {"operation_mode": "decoupled"},
            },
        )

    def _parse_aqara_attributes(self, value):
        """Parse Aqara attributes from the value."""
        if isinstance(value, str):
            value = base64.b64decode(value)

        if isinstance(value, bytes):
            try:
                skey = int(value[0])
                # Continue parsing the rest of the attributes as needed
                # ...
            except (ValueError, IndexError) as e:
                skey = 0
                print(f"Error parsing attribute value: {e}")

        return super()._parse_aqara_attributes(value)

    def _get_event_name(self, event_type):
        """Generate a unique event name."""
        return f"{self.endpoint.device.ieee}_{event_type}"
        
            
(
    QuirkBuilder("LUMI", "lumi.switch.b1naus01")
    .adds(OppleSwitchCluster, endpoint_id=1)
#    .adds(b1naus01.MultistateInputCluster, endpoint_id=1)
#    .adds(EventableOnOffCluster, endpoint_id=1)
    .adds(WallSwitchOnOffCluster, endpoint_id=1)
    .switch(
        OppleSwitchCluster.AttributeDefs.operation_mode.name,
        OppleSwitchCluster.cluster_id,
        force_inverted=True,
        translation_key="decouple_mode",
        fallback_name="Decoupled Mode"
     )
    .skip_configuration(skip_configuration=False)
    .add_to_registry()
)
