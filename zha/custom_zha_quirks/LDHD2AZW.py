"""Custom Device Handler for Leedarson LDHD2AZW contact sensor."""


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
    PollControl,
)

from zhaquirks import Bus, PowerConfigurationCluster
from zhaquirks.const import (
    ARGS,
    COMMAND,
    COMMAND_OFF,
    COMMAND_ON,
    COMMAND_STEP,
    DEVICE_TYPE,
    DIM_DOWN,
    DIM_UP,
    DOUBLE_PRESS,
    ENDPOINTS,
    INPUT_CLUSTERS,
    LONG_PRESS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PARAMS,
    PROFILE_ID,
    SHORT_PRESS,
    TURN_OFF,
    TURN_ON,
    ZHA_SEND_EVENT,
)

class LDHD2AZW(CustomDevice):
    """Custom device representing Leedarson LDHD2AZW contact sensor."""


    
    signature = {
        #  <SimpleDescriptor endpoint=1 profile=260 device_type=0x0402
        #  input_clusters=[0, 1, 3, 32, 1062, 1280, 2821]
        #  output_clusters=[3, 25]>
        MODELS_INFO: [("Leedarson", "LDHD2AZW")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: "0x0104",
                DEVICE_TYPE: zha.DeviceType.IAS_ZONE,
                INPUT_CLUSTERS: [
                    "0x0000",
                    "0x0003",
                    "0x0020",
                    "0x0402",
                    "0x0500",
                    "0x0b05",
                    "0xfd50",
                    CustomPowerConfigurationCluster.cluster_id,
                  ],
                OUTPUT_CLUSTERS: [
                    "0x0019",CustomPowerConfigurationCluster.cluster_id,
                ],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                INPUT_CLUSTERS: [
                    "0x0000",
                    CustomPowerConfigurationCluster,
                    "0x0003",
                    "0x0020",
                    "0x0402",
                    "0x0500",
                    "0x0b05",
                    "0xfd50",
                  ],
                OUTPUT_CLUSTERS: [
                    "0x0019",CustomPowerConfigurationCluster.cluster_id,
                    
                ],
            }
        },
    }
