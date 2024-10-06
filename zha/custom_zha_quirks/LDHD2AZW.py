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

class CustomPowerConfigurationCluster(PowerConfigurationCluster):
    """Custom PowerConfigurationCluster."""

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if attrid == self.BATTERY_VOLTAGE_ATTR and value not in (0, 255):
            super()._update_attribute(
                self.BATTERY_PERCENTAGE_REMAINING,
                self._calculate_battery_percentage(value),
            )

    def _calculate_battery_percentage(self, raw_value):
        volts = raw_value / 10
        volts = max(volts, self.MIN_VOLTS)
        volts = min(volts, self.MAX_VOLTS)

        percent = round(
            ((volts - self.MIN_VOLTS) / (self.MAX_VOLTS - self.MIN_VOLTS)) * 200
        )

        self.debug(
            "Voltage [RAW]:%s [Max]:%s [Min]:%s, Battery Percent: %s",
            raw_value,
            self.MAX_VOLTS,
            self.MIN_VOLTS,
            percent / 2,
        )

        return percent
    
    signature = {
        MODELS_INFO: [("Leedarson", "LDHD2AZW"), ("Leedarson LDHD2AZW")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: "0x0104",
                DEVICE_TYPE: "0x0402",
                INPUT_CLUSTERS: [
                    "0x0000",
                    "0x0001",
                    "0x0003",
                    "0x0020",
                    "0x0402",
                    "0x0500",
                    "0x0b05",
                    "0xfd50",
                  ],
                OUTPUT_CLUSTERS: [
                    "0x0019",
                ],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                INPUT_CLUSTERS: [
                    "0x0000",
                    PowerConfigurationCluster,
                    "0x0003",
                    "0x0020",
                    "0x0402",
                    "0x0500",
                    "0x0b05",
                    "0xfd50",
                  ],
                OUTPUT_CLUSTERS: [
                    "0x0019",PowerConfigurationCluster.cluster_id,
                    
                ],
            }
        },
    }
