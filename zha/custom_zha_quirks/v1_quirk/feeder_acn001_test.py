"""Quirk for Aqara aqara.feeder.acn001."""

from __future__ import annotations

import logging
from typing import Any

from zigpy import types as t
from zigpy.profiles import zgp, zha
from zigpy.zcl import foundation
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
from zigpy.zcl.foundation import ZCLCommandDef as Command

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MANUFACTURER,
    MODEL,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)
from zhaquirks.xiaomi import XiaomiAqaraE1Cluster, XiaomiCustomDevice

# 32 bit signed integer values that are encoded in FEEDER_ATTR = 0xFFF1
FEEDING = 0x04150055
FEEDING_REPORT = 0x041502BC
PORTIONS_DISPENSED = 0x0D680055
WEIGHT_DISPENSED = 0x0D690055
ERROR_DETECTED = 0x0D0B0055
SCHEDULING_STRING = 0x080008C8
DISABLE_LED_INDICATOR = 0x04170055
CHILD_LOCK = 0x04160055
FEEDING_MODE = 0x04180055
SERVING_SIZE = 0x0E5C0055
PORTION_WEIGHT = 0x0E5F0055

FEEDER_ATTR = 0xFFF1
FEEDER_ATTR_NAME = "feeder_attr"

SCHEDULING_COMMAND = b"\x08\x00\x08\xC8"
DISABLED_SCHEDULE_ENTRY = b"\x18\x00\x55\x01"

# Fake ZCL attribute ids we can use for entities for the opple cluster
ZCL_FEEDING = 0x1388
ZCL_LAST_FEEDING_SOURCE = 0x1389
ZCL_LAST_FEEDING_SIZE = 0x138A
ZCL_PORTIONS_DISPENSED = 0x138B
ZCL_WEIGHT_DISPENSED = 0x138C
ZCL_ERROR_DETECTED = 0x138D
ZCL_DISABLE_LED_INDICATOR = 0x138E
ZCL_CHILD_LOCK = 0x138F
ZCL_FEEDING_MODE = 0x1390
ZCL_SERVING_SIZE = 0x1391
ZCL_PORTION_WEIGHT = 0x1392

AQARA_TO_ZCL: dict[int, int] = {
    FEEDING: ZCL_FEEDING,
    ERROR_DETECTED: ZCL_ERROR_DETECTED,
    DISABLE_LED_INDICATOR: ZCL_DISABLE_LED_INDICATOR,
    CHILD_LOCK: ZCL_CHILD_LOCK,
    FEEDING_MODE: ZCL_FEEDING_MODE,
    SERVING_SIZE: ZCL_SERVING_SIZE,
    PORTION_WEIGHT: ZCL_PORTION_WEIGHT,
}

ZCL_TO_AQARA: dict[int, int] = {
    ZCL_FEEDING: FEEDING,
    ZCL_DISABLE_LED_INDICATOR: DISABLE_LED_INDICATOR,
    ZCL_CHILD_LOCK: CHILD_LOCK,
    ZCL_FEEDING_MODE: FEEDING_MODE,
    ZCL_SERVING_SIZE: SERVING_SIZE,
    ZCL_PORTION_WEIGHT: PORTION_WEIGHT,
    ZCL_ERROR_DETECTED: ERROR_DETECTED,
}

LOGGER = logging.getLogger(__name__)
SCHEDULES_COUNT = 10


class FeedingSchedule(t.Struct):
    """Aqara pet feeder schedule entry."""

    days: t.uint8_t
    hour: t.uint8_t
    minute: t.uint8_t
    serving_size: t.uint8_t


class Schedule(t.Struct):
    """Aqara pet feeder schedule."""

    schedules: t.FixedList[t.uint8_t, SCHEDULES_COUNT * 4]


class AqaraFeederCluster(XiaomiAqaraE1Cluster):
    """Aqara Feeder cluster."""

    attributes = {
        0xFF01: ("schedule", t.List[FeedingSchedule]),
        0xFFF1: (FEEDER_ATTR_NAME, t.LVBytes),
    }

    server_commands = {
        0x00FE: Command(
            "set_schedule",
            {"schedule": Schedule},
            False,
        ),
    }
    client_commands = {}

    def _update_attribute(self, attrid, value):
        """Update attribute."""
        if attrid == FEEDER_ATTR:
            self._parse_feeder_attribute(value)
        super()._update_attribute(attrid, value)

    def _parse_feeder_attribute(self, value):
        """Parse the feeder attribute."""
        attribute, _ = t.int32s_be.deserialize(value[3:7])
        LOGGER.debug("AqaraFeederCluster._parse_feeder_attribute: attribute: %s", attribute)
        length, _ = t.uint8_t.deserialize(value[7:8])
        LOGGER.debug("AqaraFeederCluster._parse_feeder_attribute: length: %s", length)
        attribute_value = value[8 : (length + 8)]
        LOGGER.debug(
            "AqaraFeederCluster._parse_feeder_attribute: value: %s", attribute_value
        )

        # This section should be completed to properly update HA state
        # For now, we will just log the received data.
        LOGGER.debug(
            "AqaraFeederCluster._parse_feeder_attribute: unhandled attribute: %s value: %s",
            attribute,
            attribute_value,
        )

    def _build_feeder_attribute(
        self, attribute_id: int, value: Any = None, length: int | None = None
    ):
        """Build the Xiaomi feeder attribute."""
        LOGGER.debug(
            "AqaraFeederCluster.build_feeder_attribute: id: %s, value: %s length: %s",
            attribute_id,
            value,
            length,
        )
        self._send_sequence = ((self._send_sequence or 0) + 1) % 256
        val = bytes([0x00, 0x02, self._send_sequence])
        self._send_sequence += 1
        val += t.int32s_be(attribute_id).serialize()
        if length is not None and value is not None:
            val += t.uint8_t(length).serialize()
        if value is not None:
            if length == 1:
                val += t.uint8_t(value).serialize()
            elif length == 2:
                val += t.uint16_t_be(value).serialize()
            elif length == 4:
                val += t.uint32_t_be(value).serialize()
            else:
                val += value
        LOGGER.debug(
            "AqaraFeederCluster.build_feeder_attribute: id: %s, cooked value: %s length: %s",
            attribute_id,
            val,
            length,
        )
        return FEEDER_ATTR_NAME, val

    async def write_attributes(
        self, attributes: dict[str | int, Any], manufacturer: int | None = None
    ) -> list:
        """Write attributes to device with internal 'attributes' validation."""

        # First, check if we are trying to set the schedule.
        # The key can be the name "schedule" or the attribute ID 0xFF01.
        if "schedule" in attributes or 0xFF01 in attributes:
            schedule_list = attributes.pop("schedule", attributes.pop(0xFF01, []))
            
            payload = b""
            schedules_to_write = len(schedule_list)
            for i in range(SCHEDULES_COUNT):
                if i < schedules_to_write:
                    schedule_entry = FeedingSchedule(
                        schedule_list[i].get("days", 0),
                        schedule_list[i].get("hour", 0),
                        schedule_list[i].get("minute", 0),
                        schedule_list[i].get("size", 0),
                    )
                    payload += schedule_entry.serialize()
                else:
                    payload += DISABLED_SCHEDULE_ENTRY
            
            full_command = SCHEDULING_COMMAND + payload
            
            attrs_to_write = {FEEDER_ATTR_NAME: full_command}
            return await super().write_attributes(attrs_to_write, manufacturer)

        # If we are not setting the schedule, run the original logic for other attributes.
        attrs = {}
        for attr, value in attributes.items():
            attr_def = self.find_attribute(attr)
            if attr_def and attr_def.id in ZCL_TO_AQARA:
                attribute, cooked_value = self._build_feeder_attribute(
                    ZCL_TO_AQARA[attr_def.id],
                    value,
                    4 if attr_def.name in ["serving_size", "portion_weight"] else 1,
                )
                attrs[attribute] = cooked_value
            else:
                attrs[attr] = value

        LOGGER.debug("AqaraFeederCluster.write_attributes: %s", attrs)
        return await super().write_attributes(attrs, manufacturer)


class AqaraFeederAcn001(XiaomiCustomDevice):
    """Aqara aqara.feeder.acn001 custom device implementation."""

    signature = {
        MODEL: "aqara.feeder.acn001",
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_OUTPUT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    AqaraFeederCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Ota.cluster_id,
                ],
            },
            242: {
                PROFILE_ID: zgp.PROFILE_ID,
                DEVICE_TYPE: zgp.DeviceType.PROXY_BASIC,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [
                    GreenPowerProxy.cluster_id,
                ],
            },
        },
    }

    replacement = {
        MANUFACTURER: "Aqara",
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_OUTPUT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    AqaraFeederCluster,
                    Time.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Ota.cluster_id,
                ],
            },
            242: {
                PROFILE_ID: zgp.PROFILE_ID,
                DEVICE_TYPE: zgp.DeviceType.PROXY_BASIC,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [
                    GreenPowerProxy.cluster_id,
                ],
            },
        },
    }
