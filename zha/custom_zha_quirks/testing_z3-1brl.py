"""Device handler for Lutron Aurora Z3-1BRL."""
from typing import Any, List, Optional, Union

from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
import zigpy.types as t
from zigpy.zcl import foundation
from zigpy.zcl.clusters.general import (
    Basic,
    Groups,
    Identify,
    LevelControl,
    OnOff,
    Ota,
    PollControl,
    PowerConfiguration,
)
from zigpy.zcl.clusters.lightlink import LightLink

from zhaquirks import Bus
from zhaquirks.const import (
    ARGS,
    CLUSTER_ID,
    COMMAND,
    COMMAND_OFF,
    COMMAND_ON,
    COMMAND_MOVE,
    COMMAND_MOVE_ON_OFF,
    COMMAND_MOVE_TO_LEVEL_ON_OFF,
    COMMAND_STEP,
    DIM_DOWN,
    DIM_UP,
    DEVICE_TYPE,
    ENDPOINT_ID,
    ENDPOINTS,
    INPUT_CLUSTERS,
    LEFT,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PARAMS,
    PROFILE_ID,
    RIGHT,
    ROTATED,
    SHORT_PRESS,
    SKIP_CONFIGURATION,
    TURN_OFF,
    TURN_ON,
    ZHA_SEND_EVENT,
)


class LutronAuroraZ31BRLLevelControlCluster(CustomCluster, LevelControl):
    """Lutron Aurora Z3-1BRL LevelControl cluster."""

    def __init__(self, *args, **kwargs):
        """Init."""

        super().__init__(*args, **kwargs)

        self.endpoint.device.level_control_bus.add_listener(self)

class LutronAuroraZ31BRLManufacturerSpecificCluster(CustomCluster):
    """Lutron Aurora Z3-1BRL manufacturer-specific cluster."""

    cluster_id = 0xFC00
    name = "Lutron Manufacturer Specific"
    ep_attribute = "lutron_manufacturer_specific"

#    server_commands = {
#       0x0000: foundation.ZCLCommandDef(
#          name="command",
#            schema={
#                "param1": t.uint8_t,
#                "param2": t.uint8_t,
#                "param3": t.uint8_t,
#                "param4": t.uint8_t,
#            },
#            is_reply=False,
#            is_manufacturer_specific=True,
#        )
#    }
#
#    def handle_cluster_request(
#        self,
#        hdr: foundation.ZCLHeader,
#        args: List[Any],
#        *,
#        dst_addressing: Optional[
#            Union[t.Addressing.Group, t.Addressing.IEEE, t.Addressing.NWK]
#        ] = None,
#    ):
#        """Handle cluster request."""
#
#        if args[0] == 1:
#            self.endpoint.device.level_control_bus.listener_event(
#                "listener_event", ZHA_SEND_EVENT, COMMAND_ON, [255]
#            )
#        elif args[0] == 2:
#            self.endpoint.device.level_control_bus.listener_event(
#                "listener_event", ZHA_SEND_EVENT, COMMAND_STEP, [50]
#            )
#        elif args[0] == 3:
#            self.endpoint.device.level_control_bus.listener_event(
#                 "listener_event", ZHA_SEND_EVENT, COMMAND_STEP, [50]
#            )
#        elif args[0] == 4:
#            self.endpoint.device.level_control_bus.listener_event(
#                "listener_event", ZHA_SEND_EVENT, COMMAND_OFF, [0]
#            )         


       
class LutronAurora(CustomDevice):
    """Custom device representing Lutron Aurora Z3-1BRL."""
    
    def __init__(self, *args, **kwargs):
        """Init."""

        self.level_control_bus = Bus()

        super().__init__(*args, **kwargs)

    signature = {
        # <SimpleDescriptor endpoint=1 profile=260 device_type=2080
        # device_version=0
        # input_clusters=[0, 1, 3, 4096, 64512]
        # output_clusters=[3, 4, 6, 8, 25, 4096]
        MODELS_INFO: [
            ("Lutron", "Z3-1BRL"),
            (" Lutron", "Z3-1BRL"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID, # "profile_id": 260
                DEVICE_TYPE: zha.DeviceType.NON_COLOR_CONTROLLER, # "device_type": "0x0820"
                INPUT_CLUSTERS: [
                    Basic.cluster_id, # Basic (Endpoint id: 1, Id: 0x0000, Type: in)
                    PowerConfiguration.cluster_id, # PowerConfiguration (Endpoint id: 1, Id: 0x0001, Type: in)
                    Identify.cluster_id, # Identify (Endpoint id: 1, Id: 0x0003, Type: in)
                    LightLink.cluster_id, #LightLink (Endpoint id: 1, Id: 0x1000, Type: in)
                    0xFC00, # ManufacturerSpecificCluster (Endpoint id: 1, Id: 0xfc00, Type: in)
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id, # Identify (Endpoint id: 1, Id: 0x0003, Type: out)
                    Groups.cluster_id, # Groups (Endpoint id: 1, Id: 0x0004, Type: out)
                    OnOff.cluster_id, # OnOff (Endpoint id: 1, Id: 0x0006, Type: out)
                    LevelControl.cluster_id, # LevelControl (Endpoint id: 1, Id: 0x0008, Type: out)
                    Ota.cluster_id, # Ota (Endpoint id: 1, Id: 0x0019, Type: out)
                    LightLink.cluster_id, # LightLink (Endpoint id: 1, Id: 0x1000, Type: out)
                ],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                    PollControl.cluster_id,
                    LightLink.cluster_id,
                    0xFC00,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Groups.cluster_id,
                    OnOff.cluster_id,
                    LutronAuroraZ31BRLLevelControlCluster,
                    Ota.cluster_id,
                    LightLink.cluster_id,
                    LutronAuroraZ31BRLManufacturerSpecificCluster,
                ],
            }
        }
    }

#    device_automation_triggers = {
#        (SHORT_PRESS, TURN_ON): {
#            COMMAND: COMMAND_ON,
#            ARGS: [255],        
#        },
#        (RIGHT, DIM_UP): {
#            COMMAND: COMMAND_STEP,
#            ARGS: [0],
#            PARAMS: {},
#        },
#        (LONG_PRESS, DIM_UP): {
#            COMMAND: COMMAND_STEP,
#            ARGS: [2],
#            PARAMS: {},
#        },
#        (LEFT, DIM_DOWN): {
#            COMMAND: COMMAND_STEP,
#            ARGS: [1],
#            PARAMS: {},
#        },
#        (LONG_PRESS, DIM_DOWN): {
#            COMMAND: COMMAND_STEP,
#            ARGS: [3],
#            PARAMS: {},
#        },
#        (SHORT_PRESS, TURN_OFF): {
#            COMMAND: COMMAND_OFF,
#            ARGS: [0],
#        },        
#    }
    device_automation_triggers = {
        (SHORT_PRESS, TURN_ON): {
            COMMAND: COMMAND_MOVE_TO_LEVEL_ON_OFF,
            CLUSTER_ID: 8,
            ENDPOINT_ID: 1,
            PARAMS: {"level": 255, "transition_time": 4},
        },
        (SHORT_PRESS, TURN_OFF): {
            COMMAND: COMMAND_MOVE_TO_LEVEL_ON_OFF,
            CLUSTER_ID: 8,
            ENDPOINT_ID: 1,
            PARAMS: {"level": 0, "transition_time": 4},
        },
        (ROTATED, RIGHT): {
            COMMAND: COMMAND_MOVE_TO_LEVEL_ON_OFF,
            CLUSTER_ID: 8,
            ENDPOINT_ID: 1,
            PARAMS: {"level": 200},
        },
        (ROTATED, LEFT): {
            COMMAND: COMMAND_MOVE_TO_LEVEL_ON_OFF,
            CLUSTER_ID: 8,
            ENDPOINT_ID: 1,
            PARAMS: {"level": 100},
        },
    }
