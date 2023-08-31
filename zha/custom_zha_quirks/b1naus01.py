"""Xiaomi aqara single key wall switch devices."""
import logging

from zigpy import types as t
from zigpy.profiles import zha
from zigpy.zcl.clusters.general import (
    AnalogInput,
    Basic,
    BinaryOutput,
    DeviceTemperature,
    Groups,
    Identify,
    MultistateInput,
    OnOff,
    Ota,
    Scenes,
    Time,
)

from zhaquirks import EventableCluster
from zhaquirks.const import (
    ARGS,
    ATTRIBUTE_ID,
    ATTRIBUTE_NAME,
    BUTTON,
    BUTTON_1,
    BUTTON_2,
    CLUSTER_ID,
    COMMAND,
    COMMAND_ATTRIBUTE_UPDATED,
    COMMAND_DOUBLE,
    COMMAND_HOLD,
    COMMAND_RELEASE,
    DEVICE_TYPE,
    ENDPOINT_ID,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    SKIP_CONFIGURATION,
    VALUE,
)
from zhaquirks.xiaomi import (
    LUMI,
    BasicCluster,
    OnOffCluster,
    XiaomiCustomDevice,
    XiaomiPowerConfiguration,
)

ATTRIBUTE_ON_OFF = "on_off"
DOUBLE = "double"
HOLD = "long press"
PRESS_TYPES = {0: "long press", 1: "single", 2: "double"}
SINGLE = "single"
STATUS_TYPE_ATTR = 0x0055  # decimal = 85
XIAOMI_CLUSTER_ID = 0xFFFF
XIAOMI_DEVICE_TYPE = 0x5F01
XIAOMI_DEVICE_TYPE2 = 0x5F02
XIAOMI_DEVICE_TYPE3 = 0x5F03

_LOGGER = logging.getLogger(__name__)

# click attr 0xF000
# single click 0x3FF1F00
# double click 0xCFF1F00


class BasicClusterDecoupled(BasicCluster):
    """Adds attributes for decoupled mode."""

    # Known Options for 'decoupled_mode_<button>':
    # * 254 (decoupled)
    # * 18 (relay controlled)
    attributes = BasicCluster.attributes.copy()
    attributes.update(
        {
            0xFF22: ("decoupled_mode_left", t.uint8_t, True),
            0xFF23: ("decoupled_mode_right", t.uint8_t, True),
        }
    )


class WallSwitchOnOffCluster(EventableCluster, OnOff):
    """WallSwitchOnOffCluster: fire events corresponding to press type."""


class CtrlNeutral(XiaomiCustomDevice):
    """Aqara single key switch device."""

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
        SKIP_CONFIGURATION: True,
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
                    0x0b04,
                    BasicClusterDecoupled,
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

