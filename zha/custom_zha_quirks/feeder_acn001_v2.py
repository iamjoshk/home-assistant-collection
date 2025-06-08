"""Quirk for Aqara aqara.feeder.acn001."""

from __future__ import annotations

import logging

from typing import Any

from zigpy import types
from zigpy.zcl import foundation
from zigpy.profiles import zgp, zha
from zigpy.quirks import CustomEndpoint
from zigpy.quirks.v2 import QuirkBuilder, CustomDeviceV2
from zigpy.types import t, LVBytes
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
    ENDPOINTS,
    ENDPOINT_ID,
    INPUT_CLUSTERS,
    MANUFACTURER,
    OUTPUT_CLUSTERS,
    PRESS_TYPE,
    PROFILE_ID,
    VALUE,
    ZHA_SEND_EVENT,
)
from zhaquirks.xiaomi import XiaomiCluster, XiaomiAqaraE1Cluster, XiaomiCustomDevice



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
ZCL_SCHEDULING_STRING = 0x1393

AQARA_TO_ZCL: dict[int, int] = {
    FEEDING: ZCL_FEEDING,
    ERROR_DETECTED: ZCL_ERROR_DETECTED,
    DISABLE_LED_INDICATOR: ZCL_DISABLE_LED_INDICATOR,
    CHILD_LOCK: ZCL_CHILD_LOCK,
    FEEDING_MODE: ZCL_FEEDING_MODE,
    SERVING_SIZE: ZCL_SERVING_SIZE,
    PORTION_WEIGHT: ZCL_PORTION_WEIGHT,
    SCHEDULING_STRING: ZCL_SCHEDULING_STRING,
}

ZCL_TO_AQARA: dict[int, int] = {
    ZCL_FEEDING: FEEDING,
    ZCL_DISABLE_LED_INDICATOR: DISABLE_LED_INDICATOR,
    ZCL_CHILD_LOCK: CHILD_LOCK,
    ZCL_FEEDING_MODE: FEEDING_MODE,
    ZCL_SERVING_SIZE: SERVING_SIZE,
    ZCL_PORTION_WEIGHT: PORTION_WEIGHT,
    ZCL_ERROR_DETECTED: ERROR_DETECTED,
    ZCL_SCHEDULING_STRING: SCHEDULING_STRING,
}

LOGGER = logging.getLogger(__name__)

class AqaraFeederAcn001(CustomDeviceV2):
    """Aqara aqara.feeder.acn001 custom device implementation."""

class OppleCluster(XiaomiAqaraE1Cluster):
    """Opple cluster."""

    class FeedingSource(types.enum8):
        """Feeding source."""

        Feeder = 0x01
        Remote = 0x02

    class FeedingMode(types.enum8):
        """Feeding mode."""

        Manual = 0x00
        Schedule = 0x01

    attributes = {
        ZCL_FEEDING: ("feeding", types.Bool, True),
        ZCL_LAST_FEEDING_SOURCE: ("last_feeding_source", FeedingSource, True),
        ZCL_LAST_FEEDING_SIZE: ("last_feeding_size", types.uint8_t, True),
        ZCL_PORTIONS_DISPENSED: ("portions_dispensed", types.uint16_t, True),
        ZCL_WEIGHT_DISPENSED: ("weight_dispensed", types.uint32_t, True),
        ZCL_ERROR_DETECTED: ("error_detected", types.Bool, True),
        ZCL_DISABLE_LED_INDICATOR: ("disable_led_indicator", types.Bool, True),
        ZCL_CHILD_LOCK: ("child_lock", types.Bool, True),
        ZCL_FEEDING_MODE: ("feeding_mode", FeedingMode, True),
        ZCL_SERVING_SIZE: ("serving_size", types.uint8_t, True),
        ZCL_PORTION_WEIGHT: ("portion_weight", types.uint8_t, True),
        ZCL_SCHEDULING_STRING: ("scheduling_string", types.uint8_t, True),
        FEEDER_ATTR: (FEEDER_ATTR_NAME, types.LVBytes, True),
    }

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self._send_sequence: int = None
        self._attr_cache: dict[int, Any] = {
            ZCL_DISABLE_LED_INDICATOR: False,
            ZCL_CHILD_LOCK: False,
            ZCL_FEEDING_MODE: self.FeedingMode.Manual,
            ZCL_SERVING_SIZE: 1,
            ZCL_PORTION_WEIGHT: 8,
            ZCL_ERROR_DETECTED: False,
            ZCL_PORTIONS_DISPENSED: 0,
            ZCL_WEIGHT_DISPENSED: 0,
            ZCL_SECHEDULING_STRING: 0,
        }

    def _update_attribute(self, attrid: int, value: Any) -> None:
        super()._update_attribute(attrid, value)
        LOGGER.debug(
            "OppleCluster._update_attribute: %s, %s",
            self.attributes.get(attrid).name
            if self.attributes.get(attrid) is not None
            else attrid,
            value.name if isinstance(value, types.enum8) else value,
        )
        if attrid == FEEDER_ATTR:
            self._parse_feeder_attribute(value)

    def _update_feeder_attribute(self, attrid: int, value: Any) -> None:
        zcl_attr_def = self.attributes.get(AQARA_TO_ZCL[attrid])
        self._update_attribute(zcl_attr_def.id, zcl_attr_def.type.deserialize(value)[0])

    def _parse_feeder_attribute(self, value: bytes) -> None:
        """Parse the feeder attribute."""
        attribute, _ = types.int32s_be.deserialize(value[3:7])
        LOGGER.debug("OppleCluster._parse_feeder_attribute: attribute: %s", attribute)
        length, _ = types.uint8_t.deserialize(value[7:8])
        LOGGER.debug("OppleCluster._parse_feeder_attribute: length: %s", length)
        attribute_value = value[8 : (length + 8)]
        LOGGER.debug("OppleCluster._parse_feeder_attribute: value: %s", attribute_value)

        if attribute in AQARA_TO_ZCL:
            self._update_feeder_attribute(attribute, attribute_value)
        elif attribute == FEEDING_REPORT:
            attr_str = attribute_value.decode("utf-8")
            feeding_source = attr_str[0:2]
            feeding_size = attr_str[3:4]
            self._update_attribute(
                ZCL_LAST_FEEDING_SOURCE, OppleCluster.FeedingSource(feeding_source)
            )
            self._update_attribute(ZCL_LAST_FEEDING_SIZE, int(feeding_size, base=16))
        elif attribute == PORTIONS_DISPENSED:
            portions_per_day, _ = types.uint16_t_be.deserialize(attribute_value)
            self._update_attribute(ZCL_PORTIONS_DISPENSED, portions_per_day)
        elif attribute == WEIGHT_DISPENSED:
            weight_per_day, _ = types.uint32_t_be.deserialize(attribute_value)
            self._update_attribute(ZCL_WEIGHT_DISPENSED, weight_per_day)
        elif attribute == SCHEDULING_STRING:
            scheduling_string, _ = types.uint8_t_be.deserialiaze(attribute_value)
            LOGGER.debug(
                "OppleCluster._parse_feeder_attribute: schedule not currently handled: attribute: %s value: %s",
                attribute,
                attribute_value,
            )
        else:
            LOGGER.debug(
                "OppleCluster._parse_feeder_attribute: unhandled attribute: %s value: %s",
                attribute,
                attribute_value,
            )

    def _build_feeder_attribute(
        self, attribute_id: int, value: Any = None, length: int | None = None
    ):
        """Build the Xiaomi feeder attribute."""
        LOGGER.debug(
            "OppleCluster.build_feeder_attribute: id: %s, value: %s length: %s",
            attribute_id,
            value,
            length,
        )
        self._send_sequence = ((self._send_sequence or 0) + 1) % 256
        val = bytes([0x00, 0x02, self._send_sequence])
        self._send_sequence += 1
        val += types.int32s_be(attribute_id).serialize()
        if length is not None and value is not None:
            val += types.uint8_t(length).serialize()
        if value is not None:
            if length == 1:
                val += types.uint8_t(value).serialize()
            elif length == 2:
                val += types.uint16_t_be(value).serialize()
            elif length == 4:
                val += types.uint32_t_be(value).serialize()
            else:
                val += value
        LOGGER.debug(
            "OppleCluster.build_feeder_attribute: id: %s, cooked value: %s length: %s",
            attribute_id,
            val,
            length,
        )
        return FEEDER_ATTR_NAME, val

    async def write_attributes(
        self, attributes: dict[str | int, Any], manufacturer: int | None = None
    ) -> list:
        """Write attributes to device with internal 'attributes' validation."""
        attrs = {}
        for attr, value in attributes.items():
            attr_def = self.find_attribute(attr)
            attr_id = attr_def.id
            if attr_id in ZCL_TO_AQARA:
                attribute, cooked_value = self._build_feeder_attribute(
                    ZCL_TO_AQARA[attr_id],
                    value,
                    4 if attr_def.name in ["serving_size", "portion_weight"] else 1,
                )
                attrs[attribute] = cooked_value
            else:
                attrs[attr] = value
        LOGGER.debug("OppleCluster.write_attributes: %s", attrs)
        return await super().write_attributes(attrs, manufacturer)

    async def write_attributes_raw(
        self, attrs: list[foundation.Attribute], manufacturer: int | None = None
    ) -> list:
        """Write attributes to device without internal 'attributes' validation."""
        # intentionally skip attr cache because of the encoding from Xiaomi and
        # the attributes are reported back by the device
        return await self._write_attributes(attrs, manufacturer=manufacturer)





(
    QuirkBuilder("Aqara", "aqara.feeder.acn001")
    .device_class(AqaraFeederAcn001)
    .skip_configuration(skip_configuration=False)
    .add_to_registry()
)

