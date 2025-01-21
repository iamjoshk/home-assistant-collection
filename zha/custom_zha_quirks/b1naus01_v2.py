"""Xiaomi aqara single rocker switch devices."""
from zigpy.quirks.v2 import QuirkBuilder, EntityType, NumberDeviceClass
from zigpy.types import enum
from zigpy.zcl.clusters.general import (
    Basic,
    GreenPowerProxy,
    Groups,
    Identify,
    OnOff,
    Ota,
    Scenes,
    Time,
)

class OppleOperationMode(enum.Enum8):
    """Opple operation_mode enum."""
    Decoupled = 0x00
    Coupled = 0x01

# Using QuirkBuilder to create the quirk
(
    QuirkBuilder("LUMI", "lumi.switch.b1naus01")
    # Define the operation mode attribute
    .enum(
        attribute_name="operation_mode",
        enum_class=OppleOperationMode,
        cluster_id=0xFCC0,  # OppleSwitchCluster
        endpoint_id=1,
        entity_platform="select",
        entity_type=EntityType.CONFIG,
        translation_key="operation_mode",
        fallback_name="Operation Mode"
    )
    # Add required clusters
    .replacement(
        {
            "endpoints": {
                1: {
                    "device_type": 0x0100,  # zha.DeviceType.ON_OFF_LIGHT
                    "input_clusters": [
                        Basic.cluster_id,
                        "DeviceTemperatureCluster",
                        Identify.cluster_id,
                        Groups.cluster_id,
                        Scenes.cluster_id,
                        "OnOffCluster",
                        "MultistateInputCluster",
                        "XiaomiMeteringCluster",
                        0xFCC0,  # OppleSwitchCluster
                        0x0B04,
                    ],
                    "output_clusters": [
                        Time.cluster_id,
                        Ota.cluster_id,
                    ],
                },
                41: {
                    "device_type": 0x0000,  # zha.DeviceType.ON_OFF_SWITCH
                    "input_clusters": [
                        "MultistateInputCluster",
                    ],
                    "output_clusters": [],
                },
                242: {
                    "profile_id": 0xA1E0,  # zgp.PROFILE_ID
                    "device_type": 0x0061,  # zgp.DeviceType.PROXY_BASIC
                    "input_clusters": [],
                    "output_clusters": [
                        GreenPowerProxy.cluster_id,
                    ],
                },
            }
        }
    )
    # Add device automation triggers
    .device_automation_triggers(
        {
            ("button_single", "button"): {
                "endpoint_id": 41,
                "cluster_id": 18,
                "params": {"attr_id": 0x0055, "press_type": "single", "value": 1},
            },
            ("button_double", "button"): {
                "endpoint_id": 41,
                "cluster_id": 18,
                "params": {"attr_id": 0x0055, "press_type": "double", "value": 2},
            },
            ("button_hold", "button"): {
                "endpoint_id": 1,
                "cluster_id": 0xFCC0,
                "params": {"attr_id": 0x00FC, "press_type": "hold", "value": 0},
            },
        }
    )
    .add_to_registry()
)
