"""Xiaomi aqara single rocker switch devices."""
import logging                                                 
from zigpy.profiles import zgp, zha
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import (
    Alarms,
    Basic,
    GreenPowerProxy,
    Groups,
    Identify,
    OnOff,
    Ota,
    Scenes,
    Time,
)

from zhaquirks.const import (
    ARGS,
    ATTR_ID,
    BUTTON,
    CLUSTER_ID,
    COMMAND,
    COMMAND_DOUBLE,
    COMMAND_HOLD,
    COMMAND_SINGLE,
    DEVICE_TYPE,
    DOUBLE_PRESS,
    ENDPOINT_ID,
    ENDPOINTS,
    INPUT_CLUSTERS,
    LONG_PRESS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PRESS_TYPE,
    PROFILE_ID,
    SHORT_PRESS,
    VALUE,
)
from zhaquirks.xiaomi import (
    LUMI,
    BasicCluster,
    DeviceTemperatureCluster,
    OnOffCluster,
    XiaomiMeteringCluster,
)
from zhaquirks.xiaomi.aqara.opple_remote import MultistateInputCluster
from zhaquirks.xiaomi.aqara.opple_switch import OppleSwitchCluster

XIAOMI_COMMAND_SINGLE = "41_single"
XIAOMI_COMMAND_DOUBLE = "41_double"
XIAOMI_COMMAND_HOLD = "1_hold"


class AqaraUSC03SingleRocker(CustomDevice):
    """Device automation triggers for the Aqara WS-USC03 Single Rocker Switches"""

    device_automation_triggers = {
        (SHORT_PRESS, BUTTON): {
            ENDPOINT_ID: 41,
            CLUSTER_ID: 18,
            COMMAND: XIAOMI_COMMAND_SINGLE,
            ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_SINGLE, VALUE: 1},
        },
        (DOUBLE_PRESS, BUTTON): {
            ENDPOINT_ID: 41,
            CLUSTER_ID: 18,
            COMMAND: XIAOMI_COMMAND_DOUBLE,
            ARGS: {ATTR_ID: 0x0055, PRESS_TYPE: COMMAND_DOUBLE, VALUE: 2},
        },
        (LONG_PRESS, BUTTON): {
            ENDPOINT_ID: 1,
            CLUSTER_ID: 64704,
            COMMAND: XIAOMI_COMMAND_HOLD,
            ARGS: {ATTR_ID: 0x00FC, PRESS_TYPE: COMMAND_HOLD, VALUE: 0},
        },
    }


class AqaraUSC03SingleRockerSwitchWithNeutral(AqaraUSC03SingleRocker):
    """Aqara WS-USC03 Single Rocker Switch (with neutral)."""

    signature = {
        MODELS_INFO: [
            ("LUMI", "lumi.switch.b1naus01"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: 0x0104,
                DEVICE_TYPE: 0x0100,
                INPUT_CLUSTERS: [
                    0x0000,
                    0x0002,
                    0x0003,
                    0x0004,
                    0x0005,
                    0x0006,
                    0x0009,
                    0x0702,
                    0x0b04
                ],
                OUTPUT_CLUSTERS: [
                    0x000a,
                    0x0019
                ]
            },
            242: {
                PROFILE_ID: 0xa1e0,
                DEVICE_TYPE: 0x0061,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [
                    0x0021
                ]
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    BasicCluster,  # 0
                    DeviceTemperatureCluster.cluster_id,  # 2
                    Identify.cluster_id,  # 3
                    Groups.cluster_id,  # 4
                    Scenes.cluster_id,  # 5
                    OnOffCluster,  # 6
                    Alarms.cluster_id,  # 9
                    MultistateInputCluster,  # 18
                    XiaomiMeteringCluster.cluster_id,  # 0x0702
                    OppleSwitchCluster,  # 0xFCC0 / 64704
                    0x0B04,
                ],
                OUTPUT_CLUSTERS: [
                    Time.cluster_id,
                    Ota.cluster_id,
                ],
            },
            41: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_SWITCH,
                INPUT_CLUSTERS: [
                    MultistateInputCluster,  # 18
                ],
                OUTPUT_CLUSTERS: [],
            },
            242: {
                PROFILE_ID: zgp.PROFILE_ID,
                DEVICE_TYPE: zgp.DeviceType.PROXY_BASIC,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            },
        },
    }

