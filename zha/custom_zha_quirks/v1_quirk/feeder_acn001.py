"""Quirk for Aqara aqara.feeder.acn001."""

from __future__ import annotations

import ast
import json
import logging
import time
from typing import Any

from zigpy import types
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

from zhaquirks import EventableCluster
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
SCHEDULING = 0x080008C8
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
ZCL_SCHEDULE = 0x1393

AQARA_TO_ZCL: dict[int, int] = {
    FEEDING: ZCL_FEEDING,
    ERROR_DETECTED: ZCL_ERROR_DETECTED,
    DISABLE_LED_INDICATOR: ZCL_DISABLE_LED_INDICATOR,
    CHILD_LOCK: ZCL_CHILD_LOCK,
    FEEDING_MODE: ZCL_FEEDING_MODE,
    SERVING_SIZE: ZCL_SERVING_SIZE,
    PORTION_WEIGHT: ZCL_PORTION_WEIGHT,
    SCHEDULING: ZCL_SCHEDULE,
}

ZCL_TO_AQARA: dict[int, int] = {
    ZCL_FEEDING: FEEDING,
    ZCL_DISABLE_LED_INDICATOR: DISABLE_LED_INDICATOR,
    ZCL_CHILD_LOCK: CHILD_LOCK,
    ZCL_FEEDING_MODE: FEEDING_MODE,
    ZCL_SERVING_SIZE: SERVING_SIZE,
    ZCL_PORTION_WEIGHT: PORTION_WEIGHT,
    ZCL_ERROR_DETECTED: ERROR_DETECTED,
    ZCL_SCHEDULE: SCHEDULING,
}

LOGGER = logging.getLogger(__name__)

# Day mapping based on Z2M implementation
DAYS_MAP = {
    'everyday': 0x7F,    # 127
    'workdays': 0x1F,    # 31  
    'weekend': 0x60,     # 96
    'mon': 0x01,         # 1
    'tue': 0x02,         # 2
    'wed': 0x04,         # 4
    'thu': 0x08,         # 8
    'fri': 0x10,         # 16
    'sat': 0x20,         # 32
    'sun': 0x40,         # 64
}


class OppleCluster(XiaomiAqaraE1Cluster, EventableCluster):
    """Opple cluster with event support."""

    class FeedingSource(types.enum8):
        """Feeding source."""

        Schedule = 0x00
        Manual = 0x01
        Remote = 0x02

    class FeedingMode(types.enum8):
        """Feeding mode."""

        Manual = 0x00
        Schedule = 0x01

    # Mark all custom attributes as reportable to ensure entities are created
    attributes = {
        ZCL_FEEDING: foundation.ZCLAttributeDef(
            id=ZCL_FEEDING, name="feeding", type=types.Bool, access="rps"
        ),
        ZCL_LAST_FEEDING_SOURCE: foundation.ZCLAttributeDef(
            id=ZCL_LAST_FEEDING_SOURCE, name="last_feeding_source", type=FeedingSource, access="rps"
        ),
        ZCL_LAST_FEEDING_SIZE: foundation.ZCLAttributeDef(
            id=ZCL_LAST_FEEDING_SIZE, name="last_feeding_size", type=types.uint8_t, access="rps"
        ),
        ZCL_PORTIONS_DISPENSED: foundation.ZCLAttributeDef(
            id=ZCL_PORTIONS_DISPENSED, name="portions_dispensed", type=types.uint16_t, access="rps"
        ),
        ZCL_WEIGHT_DISPENSED: foundation.ZCLAttributeDef(
            id=ZCL_WEIGHT_DISPENSED, name="weight_dispensed", type=types.uint32_t, access="rps"
        ),
        ZCL_ERROR_DETECTED: foundation.ZCLAttributeDef(
            id=ZCL_ERROR_DETECTED, name="error_detected", type=types.Bool, access="rps"
        ),
        ZCL_DISABLE_LED_INDICATOR: foundation.ZCLAttributeDef(
            id=ZCL_DISABLE_LED_INDICATOR, name="disable_led_indicator", type=types.Bool, access="rps"
        ),
        ZCL_CHILD_LOCK: foundation.ZCLAttributeDef(
            id=ZCL_CHILD_LOCK, name="child_lock", type=types.Bool, access="rps"
        ),
        ZCL_FEEDING_MODE: foundation.ZCLAttributeDef(
            id=ZCL_FEEDING_MODE, name="feeding_mode", type=FeedingMode, access="rps"
        ),
        ZCL_SERVING_SIZE: foundation.ZCLAttributeDef(
            id=ZCL_SERVING_SIZE, name="serving_size", type=types.uint8_t, access="rps"
        ),
        ZCL_PORTION_WEIGHT: foundation.ZCLAttributeDef(
            id=ZCL_PORTION_WEIGHT, name="portion_weight", type=types.uint8_t, access="rps"
        ),
        ZCL_SCHEDULE: foundation.ZCLAttributeDef(
            id=ZCL_SCHEDULE, name="schedule", type=types.CharacterString, access="rps"
        ),
        FEEDER_ATTR: foundation.ZCLAttributeDef(
            id=FEEDER_ATTR, name=FEEDER_ATTR_NAME, type=types.LVBytes, access="rps"
        ),
        # Add the unknown attribute to prevent crashes
        0x00F7: foundation.ZCLAttributeDef(
            id=0x00F7, name="status_report", type=types.LVBytes, access="rps"
        ),
    }

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self._send_sequence: int = 0
        # Track recently written values to prevent device overrides
        self._recently_written: dict[int, Any] = {}
        self._write_timestamps: dict[int, float] = {}
        self._attributes_initialized = False
        
        # Simple cache like the working example - with proper enum values
        self._attr_cache: dict[int, Any] = {
            ZCL_FEEDING: False,
            ZCL_LAST_FEEDING_SOURCE: self.FeedingSource.Manual,
            ZCL_LAST_FEEDING_SIZE: 0,
            ZCL_PORTIONS_DISPENSED: 0,
            ZCL_WEIGHT_DISPENSED: 0,
            ZCL_ERROR_DETECTED: False,
            ZCL_DISABLE_LED_INDICATOR: False,
            ZCL_CHILD_LOCK: False,
            ZCL_FEEDING_MODE: self.FeedingMode.Manual,
            ZCL_SERVING_SIZE: 1,
            ZCL_PORTION_WEIGHT: 8,
            ZCL_SCHEDULE: "[]",
        }

    def _initialize_attributes(self):
        """Initialize all custom attributes with default values."""
        if self._attributes_initialized:
            return
            
        nwk = self._get_device_nwk()
        LOGGER.debug("[0x%04X] Initializing feeder attributes", nwk)
        
        # Initialize all attributes with defaults
        for attr_id, default_value in self._attr_cache.items():
            try:
                # Update both our cache and parent cache
                super()._update_attribute(attr_id, default_value)
                LOGGER.debug(
                    "[0x%04X] Initialized attribute %s (0x%04X) with default: %s", 
                    nwk, self._get_attribute_name(attr_id), attr_id, default_value
                )
            except Exception as e:
                LOGGER.debug("[0x%04X] Error initializing attribute 0x%04X: %s", nwk, attr_id, e)
        
        self._attributes_initialized = True

    def _get_device_nwk(self) -> int:
        """Get device network address safely."""
        try:
            return self._endpoint.device.nwk
        except Exception:
            return 0

    def _is_recently_written(self, attr_id: int) -> bool:
        """Check if attribute was recently written (within 10 seconds)."""
        if attr_id not in self._write_timestamps:
            return False
        return (time.time() - self._write_timestamps[attr_id]) < 10.0

    def _mark_as_written(self, attr_id: int, value: Any) -> None:
        """Mark attribute as recently written."""
        self._recently_written[attr_id] = value
        self._write_timestamps[attr_id] = time.time()

    def _get_attribute_name(self, attrid: int) -> str:
        """Get attribute name safely from different attribute definition formats."""
        try:
            attr_def = self.attributes.get(attrid)
            if attr_def is None:
                return f"attr_{attrid:04X}"
            
            # Handle tuple format (name, type, access)
            if isinstance(attr_def, tuple) and len(attr_def) >= 1:
                return attr_def[0]
            
            # Handle ZCLAttributeDef object
            if hasattr(attr_def, 'name'):
                return attr_def.name
            
            # Handle other formats
            if hasattr(attr_def, 'id'):
                return f"attr_{attr_def.id:04X}"
            
            return f"attr_{attrid:04X}"
        except Exception:
            return f"attr_{attrid:04X}"

    def _fire_attribute_event(self, attrid: int, attr_name: str, old_value: Any, new_value: Any) -> None:
        """Fire ZHA event for attribute changes using EventableCluster."""
        nwk = self._get_device_nwk()
        LOGGER.info("[0x%04X] _fire_attribute_event called: attr=0x%04X, old=%s, new=%s", 
                   nwk, attrid, old_value, new_value)
        
        try:
            # Handle the raw feeder attribute specially - it's used for confirmations
            if attrid == FEEDER_ATTR:
                LOGGER.debug("[0x%04X] Processing feeder attribute response for confirmation", nwk)
                
                # Convert LVBytes to hex string for JSON serialization
                def make_json_safe(value):
                    """Convert value to JSON-safe format."""
                    if hasattr(value, 'name'):
                        return value.name
                    elif isinstance(value, bytes):
                        return value.hex()
                    elif hasattr(value, '__bytes__'):
                        return bytes(value).hex()
                    else:
                        return str(value)
                
                old_hex = make_json_safe(old_value) if old_value else ""
                new_hex = make_json_safe(new_value)
                
                # Fire a device response confirmation event
                try:
                    confirmation_args = {
                        "attribute_id": attrid,
                        "attribute_name": attr_name,
                        "old_value": old_hex,
                        "new_value": new_hex,
                        "response_length": len(new_value) if isinstance(new_value, (bytes, types.LVBytes)) else 0,
                    }
                    
                    # Try to parse the response to add more context
                    if isinstance(new_value, (bytes, types.LVBytes)) and len(new_value) >= 8:
                        try:
                            # Extract the attribute ID from the response
                            response_attr_id, _ = types.int32s_be.deserialize(bytes(new_value)[3:7])
                            confirmation_args["response_attribute_id"] = f"0x{response_attr_id:08X}"
                            
                            # Map to human-readable attribute name
                            attr_names = {
                                FEEDING: "feeding",
                                ERROR_DETECTED: "error_detected",
                                DISABLE_LED_INDICATOR: "disable_led_indicator", 
                                CHILD_LOCK: "child_lock",
                                FEEDING_MODE: "feeding_mode",
                                SERVING_SIZE: "serving_size",
                                PORTION_WEIGHT: "portion_weight",
                                SCHEDULING: "scheduling",
                                FEEDING_REPORT: "feeding_report",
                                PORTIONS_DISPENSED: "portions_dispensed",
                                WEIGHT_DISPENSED: "weight_dispensed"
                            }
                            confirmation_args["response_attribute_name"] = attr_names.get(response_attr_id, "unknown")
                            
                        except Exception as parse_error:
                            LOGGER.debug("[0x%04X] Could not parse response details: %s", nwk, parse_error)
                    
                    self.listener_event("zha_event", "device_response_received", confirmation_args)
                    LOGGER.info("[0x%04X] Fired device response confirmation event", nwk)
                    
                except Exception as e:
                    LOGGER.error("[0x%04X] Error firing confirmation event: %s", nwk, e, exc_info=True)
                
                return  # Don't process further for raw feeder attribute
            
            # Only fire events for user-relevant attributes
            important_attrs = {
                ZCL_SCHEDULE: "schedule_updated",
                ZCL_FEEDING_MODE: "feeding_mode_changed", 
                ZCL_CHILD_LOCK: "child_lock_changed",
                ZCL_DISABLE_LED_INDICATOR: "led_indicator_changed",
                ZCL_SERVING_SIZE: "serving_size_changed",
                ZCL_PORTION_WEIGHT: "portion_weight_changed",
                ZCL_LAST_FEEDING_SOURCE: "feeding_occurred",
                ZCL_ERROR_DETECTED: "error_detected"
            }
            
            if attrid in important_attrs:
                event_type = important_attrs[attrid]
                LOGGER.info("[0x%04X] Preparing to fire event: %s", nwk, event_type)
                
                # Format values for the event - make them JSON serializable
                def make_json_safe(value):
                    """Convert value to JSON-safe format."""
                    if hasattr(value, 'name'):
                        return value.name
                    elif isinstance(value, bytes):
                        return value.hex()
                    elif hasattr(value, '__bytes__'):
                        return bytes(value).hex()
                    else:
                        return str(value)
                
                old_str = make_json_safe(old_value)
                new_str = make_json_safe(new_value)
                
                # Prepare event args - all JSON serializable
                event_args = {
                    "attribute_id": attrid,
                    "attribute_name": attr_name,
                    "old_value": old_str,
                    "new_value": new_str,
                }
                
                # Check if this change was recently written (i.e., it's a confirmation)
                if self._is_recently_written(attrid):
                    event_args["is_confirmation"] = True
                    event_args["write_timestamp"] = self._write_timestamps.get(attrid, 0)
                else:
                    event_args["is_confirmation"] = False
                
                # Special handling for schedule events
                if attrid == ZCL_SCHEDULE and isinstance(new_value, str):
                    try:
                        schedule_data = json.loads(new_value) if new_value.strip() else []
                        event_args["schedule_entries"] = len(schedule_data)
                        event_args["schedule_data"] = schedule_data
                    except:
                        pass
                
                LOGGER.info("[0x%04X] Event args prepared: %s", nwk, event_args)
                
                # Use EventableCluster's listener_event method (the correct method)
                try:
                    self.listener_event("zha_event", event_type, event_args)
                    LOGGER.info("[0x%04X] Successfully fired ZHA event via EventableCluster: %s", nwk, event_type)
                        
                except Exception as event_error:
                    LOGGER.error("[0x%04X] Failed to fire event via EventableCluster: %s", nwk, event_error, exc_info=True)
                    
            else:
                LOGGER.debug("[0x%04X] Attribute 0x%04X not in important_attrs", nwk, attrid)
                
        except Exception as e:
            LOGGER.error("[0x%04X] Error in _fire_attribute_event: %s", nwk, e, exc_info=True)

    def _update_attribute(self, attrid: int, value: Any) -> None:
        """Update attribute with proper listener notification."""
        nwk = self._get_device_nwk()
        LOGGER.debug("[0x%04X] _update_attribute called: attr=0x%04X, value=%s", nwk, attrid, value)
        
        # Special handling for the status report - just log and store for future investigation
        if attrid == 0x00F7 and isinstance(value, (bytes, types.LVBytes)):
            raw_value = bytes(value)
            LOGGER.debug("[0x%04X] Status report 0x00F7: %s", nwk, raw_value.hex())
            # Store it but don't analyze further for now
            if hasattr(self, '_attr_cache'):
                self._attr_cache[attrid] = raw_value
            if hasattr(self, '_attributes'):
                self._attributes[attrid] = raw_value.hex()
            return
        
        # Special handling for main feeder attribute
        if attrid == FEEDER_ATTR and isinstance(value, (bytes, types.LVBytes)):
            raw_value = bytes(value)
            old_value = self._attr_cache.get(attrid) if hasattr(self, '_attr_cache') else None
            
            if hasattr(self, '_attr_cache'):
                self._attr_cache[attrid] = raw_value
                
            # Parse the feeder attribute normally
            self._parse_feeder_attribute(raw_value)
            
            # Call parent to update the attribute (THIS WAS MISSING!)
            super()._update_attribute(attrid, raw_value.hex())  # Convert to hex string
            
            # Fire events for feeder attribute - each response is a confirmation
            attr_name = self._get_attribute_name(attrid)
            self._fire_attribute_event(attrid, attr_name, old_value, raw_value)
            return
        
        # Normal processing for other attributes
        old_value = self._attr_cache.get(attrid) if hasattr(self, '_attr_cache') else None
        
        if hasattr(self, '_attr_cache'):
            self._attr_cache[attrid] = value
        
        # Call parent to update the attribute
        super()._update_attribute(attrid, value)
        
        # Fire events if value changed
        if old_value != value:
            attr_name = self._get_attribute_name(attrid)
            self._fire_attribute_event(attrid, attr_name, old_value, value)

    def _update_feeder_attribute(self, attrid: int, value: Any) -> None:
        """Update feeder attribute with validation."""
        zcl_attr_id = AQARA_TO_ZCL.get(attrid)
        if zcl_attr_id and zcl_attr_id in self.attributes:
            zcl_attr_def = self.attributes[zcl_attr_id]
            if isinstance(zcl_attr_def, tuple):
                attr_type = zcl_attr_def[1]
                try:
                    parsed_value = attr_type.deserialize(value)[0]
                    self._update_attribute(zcl_attr_id, parsed_value)
                except Exception as e:
                    LOGGER.debug("Failed to parse %s: %s", attrid, e)

    def _parse_feeder_attribute(self, value: Any) -> None:
        """Parse the feeder attribute - simplified like working example."""
        try:
            if isinstance(value, str) and value.startswith("b'"):
                value = ast.literal_eval(value)
            
            if not isinstance(value, bytes):
                LOGGER.error("Invalid value type: %s", type(value))
                return
                
            if len(value) < 8:
                LOGGER.debug("Attribute too short: %s bytes", len(value))
                return

            # Parse like working example
            attribute, _ = types.int32s_be.deserialize(value[3:7])
            length, _ = types.uint8_t.deserialize(value[7:8])
            
            if len(value) < length + 8:
                LOGGER.debug("Incomplete attribute %s: %s < %s", 
                        attribute, len(value), length + 8)
                return
                
            attribute_value = value[8 : (length + 8)]
            nwk = self._get_device_nwk()
            LOGGER.debug("[0x%04X] Processing attr 0x%08X: %s (%s bytes)", 
                        nwk, attribute, attribute_value.hex(), len(attribute_value))

            # Handle attributes like working example
            if attribute in AQARA_TO_ZCL:
                self._update_feeder_attribute(attribute, attribute_value)
            elif attribute == FEEDING_REPORT:
                self._parse_feeding_report(attribute_value)
            elif attribute == PORTIONS_DISPENSED:
                try:
                    portions_per_day, _ = types.uint16_t_be.deserialize(attribute_value)
                    self._update_attribute(ZCL_PORTIONS_DISPENSED, portions_per_day)
                    LOGGER.debug("[0x%04X] Updated portions dispensed: %s", nwk, portions_per_day)
                except ValueError as e:
                    LOGGER.debug("Failed to parse portions: %s", e)
            elif attribute == WEIGHT_DISPENSED:
                try:
                    weight_per_day, _ = types.uint32_t_be.deserialize(attribute_value)
                    self._update_attribute(ZCL_WEIGHT_DISPENSED, weight_per_day)
                    LOGGER.info("[0x%04X] Updated weight dispensed: %s grams", nwk, weight_per_day)
                except ValueError as e:
                    LOGGER.debug("[0x%04X] Failed to parse weight: %s - raw: %s", 
                                nwk, e, attribute_value.hex())
            elif attribute == SCHEDULING:
                self._parse_schedule(attribute_value)
            else:
                LOGGER.debug("[0x%04X] Unhandled attribute: 0x%08X = %s", nwk, attribute, attribute_value.hex())

        except Exception as e:
            nwk = self._get_device_nwk()
            LOGGER.error("[0x%04X] Error parsing feeder attribute: %s", nwk, e)

    def _parse_feeding_report(self, value: bytes) -> None:
        """Parse feeding report - like working example."""
        try:
            attr_str = value.decode("utf-8")
            LOGGER.debug("Raw feeding report: %r", attr_str)
            
            if len(attr_str) >= 4:
                raw_source = attr_str[0:2]
                feeding_source = int(raw_source, 16)
                LOGGER.debug("Parsed source value: %r", feeding_source)
                
                enum_value = self.FeedingSource(feeding_source)
                LOGGER.debug("Created enum: %r (%s)", enum_value, str(enum_value))
                
                self._update_attribute(ZCL_LAST_FEEDING_SOURCE, enum_value)
                feeding_size = attr_str[3:4]
                self._update_attribute(ZCL_LAST_FEEDING_SIZE, int(feeding_size, base=16))
                
                # Fire a feeding event with additional context using EventableCluster
                try:
                    nwk = self._get_device_nwk()
                    feeding_event_args = {
                        "feeding_source": enum_value.name,
                        "feeding_size": int(feeding_size, base=16),
                        "raw_data": attr_str
                    }
                    
                    # Use EventableCluster's listener_event method
                    self.listener_event("zha_event", "feeding_completed", feeding_event_args)
                    LOGGER.info("[0x%04X] Fired feeding completed event via EventableCluster", nwk)
                    
                except Exception as e:
                    LOGGER.error("[0x%04X] Error firing feeding event: %s", nwk, e, exc_info=True)
                    
        except Exception as e:
            LOGGER.debug("Failed to parse feeding report: %s", e)

    def _parse_schedule(self, value: bytes) -> None:
        """Parse schedule from device response."""
        try:
            schedule_value = value.decode("utf-8").strip()
            LOGGER.debug("Raw schedule data: %r", schedule_value)
            
            if not schedule_value:
                self._update_attribute(ZCL_SCHEDULE, "[]")
                return
            
            # Parse hex schedules and convert to JSON
            schedules = []
            if ',' in schedule_value:
                schedule_parts = schedule_value.split(',')
            else:
                schedule_parts = schedule_value.split()
            
            for part in schedule_parts:
                part = part.strip()
                if len(part) >= 8:
                    try:
                        days_mask = int(part[0:2], 16)
                        hour = int(part[2:4], 16)
                        minute = int(part[4:6], 16)
                        portions = int(part[6:8], 16)
                        
                        # Convert days mask to day names
                        day_names = []
                        for day_name, mask in DAYS_MAP.items():
                            if days_mask == mask:
                                day_names.append(day_name)
                                break
                        
                        if day_names and hour < 24 and minute < 60 and portions > 0:
                            schedule_entry = {
                                "days": day_names[0],
                                "hour": hour,
                                "minute": minute,
                                "portions": portions
                            }
                            schedules.append(schedule_entry)
                            LOGGER.debug("Parsed schedule entry: %s", schedule_entry)
                    except (ValueError, IndexError) as e:
                        LOGGER.debug("Failed to parse schedule part %s: %s", part, e)
            
            schedule_json = json.dumps(schedules)
            self._update_attribute(ZCL_SCHEDULE, schedule_json)
            LOGGER.info("Updated schedule: %s", schedule_json)
            
        except Exception as e:
            LOGGER.error("Failed to parse schedule: %s", e)

    def _encode_schedule(self, schedule_input: Any) -> bytes | None:
        """Encode schedule to device format."""
        try:
            if isinstance(schedule_input, str):
                schedule_list = json.loads(schedule_input)
            elif isinstance(schedule_input, list):
                schedule_list = schedule_input
            else:
                LOGGER.error("Invalid schedule format: %s", type(schedule_input))
                return None

            if not isinstance(schedule_list, list) or len(schedule_list) > 5:
                LOGGER.error("Schedule must be a list with max 5 entries")
                return None
            
            schedule_parts = []
            for schedule in schedule_list:
                days = schedule.get('days', 'everyday')
                hour = schedule.get('hour', 0)
                minute = schedule.get('minute', 0)
                portions = schedule.get('portions', 1)
                
                if hour > 23 or minute > 59 or portions < 1:
                    LOGGER.error("Invalid schedule values")
                    return None
                
                days_mask = DAYS_MAP.get(days, 0x7F)
                schedule_hex = f"{days_mask:02X}{hour:02X}{minute:02X}{portions:02X}00"
                schedule_parts.append(schedule_hex)
            
            # Use working format from your example
            schedule_data = ",".join(schedule_parts)
            header = bytes([0x05, 0x15, 0x08, 0x00, 0x08, 0xc8])
            packet = header + b" " + schedule_data.encode()
            LOGGER.debug("Schedule packet: %s", packet.hex())
            return packet
            
        except Exception as e:
            LOGGER.error("Failed to encode schedule: %s", e)
            return None

    def _build_feeder_attribute(
        self, attribute_id: int, value: Any = None, length: int | None = None
    ):
        """Build the Xiaomi feeder attribute - like working example."""
        self._send_sequence = ((self._send_sequence or 0) + 1) % 256
        val = bytes([0x00, 0x02, self._send_sequence])
        val += types.int32s_be(attribute_id).serialize()
        if length is not None and value is not None:
            val += types.uint8_t(length).serialize()
            if length == 1:
                val += types.uint8_t(value).serialize()
            elif length == 2:
                val += types.uint16_t_be(value).serialize()
            elif length == 4:
                val += types.uint32_t_be(value).serialize()
            else:
                val += value
        
        LOGGER.debug("Built feeder attribute 0x%08X with value %s (length %s): %s", 
                    attribute_id, value, length, val.hex())
        return FEEDER_ATTR_NAME, val

    async def write_attributes(
        self, attributes: dict[str | int, Any], manufacturer: int | None = None
    ) -> list:
        """Write attributes to device with immediate UI feedback."""
        nwk = self._get_device_nwk()
        LOGGER.info("[0x%04X] write_attributes called with: %s", nwk, attributes)
        
        attrs = {}
        for attr, value in attributes.items():
            LOGGER.debug("[0x%04X] Processing attribute: %s = %s", nwk, attr, value)
            
            # Special handling for schedule
            if attr == ZCL_SCHEDULE or (isinstance(attr, str) and attr == "schedule"):
                try:
                    schedule_val = str(getattr(value, "value", value))
                    if schedule_val.strip():
                        packet = self._encode_schedule(schedule_val)
                        if packet:
                            # Update UI immediately AND fire event
                            old_schedule = self._attr_cache.get(ZCL_SCHEDULE, "[]")
                            self._update_attribute(ZCL_SCHEDULE, schedule_val)
                            
                            tv = foundation.TypeValue()
                            tv.type = 0x41
                            tv.value = types.LongOctetString(packet)
                            result = await self._write_attributes(
                                [foundation.Attribute(FEEDER_ATTR, tv)],
                                manufacturer=0x115F
                            )
                            LOGGER.info("[0x%04X] Schedule write result: %s", nwk, result)
                            return result
                except Exception as e:
                    LOGGER.error("Schedule processing error: %s", e, exc_info=True)
                continue

            attr_def = self.find_attribute(attr)
            if not attr_def:
                LOGGER.warning("[0x%04X] Could not find attribute definition for: %s", nwk, attr)
                continue
                
            attr_id = attr_def.id
            LOGGER.debug("[0x%04X] Found attr_id 0x%04X for %s", nwk, attr_id, attr)
            
            if attr_id in ZCL_TO_AQARA:
                # Mark as recently written
                self._mark_as_written(attr_id, value)
                
                # IMMEDIATELY update UI to prevent reverting AND fire event
                old_value = self._attr_cache.get(attr_id)
                LOGGER.info("[0x%04X] Updating attribute 0x%04X: %s -> %s", nwk, attr_id, old_value, value)
                self._update_attribute(attr_id, value)
                
                # Get attribute name safely for length determination
                attr_name = getattr(attr_def, 'name', '')
                if not attr_name and hasattr(attr_def, 'id'):
                    # Try to get from our attributes dict
                    our_attr = self.attributes.get(attr_def.id)
                    if isinstance(our_attr, tuple):
                        attr_name = our_attr[0]
                
                attr_name = getattr(attr_def, 'name', '')
                length = 4 if attr_name in ["serving_size", "portion_weight"] else 1
                
                attribute, cooked_value = self._build_feeder_attribute(
                    ZCL_TO_AQARA[attr_id],
                    value,
                    length,
                )
                attrs[attribute] = cooked_value
            else:
                LOGGER.debug("[0x%04X] Attribute 0x%04X not in ZCL_TO_AQARA", nwk, attr_id)
                attrs[attr] = value

        if attrs:
            LOGGER.info("[0x%04X] Sending %d attributes to device", nwk, len(attrs))
            result = await super().write_attributes(attrs, manufacturer=0x115F)
            LOGGER.info("[0x%04X] Write result: %s", nwk, result)
            return result
        else:
            LOGGER.warning("[0x%04X] No attributes to write!", nwk)
        return [foundation.Status.SUCCESS]

    async def write_attributes_raw(
        self, attrs: list[foundation.Attribute], manufacturer: int | None = None
    ) -> list:
        """Write attributes to device without internal 'attributes' validation."""
        return await self._write_attributes(attrs, manufacturer=manufacturer)

    async def write_attributes_safe(
        self, attributes: dict[str | int, Any], manufacturer: int | None = None
    ) -> list:
        """Use same attribute handling as write_attributes."""
        return await self.write_attributes(attributes, manufacturer)


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
                    OppleCluster.cluster_id,
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
                    OppleCluster,
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
    
    async def configure(self):
        """Configure the device."""
        try:
            await super().configure()
            
            # Get the OppleCluster and initialize it
            opple_cluster = self.endpoints[1].in_clusters.get(OppleCluster.cluster_id)
            if opple_cluster:
                nwk = getattr(self, 'nwk', 0)
                LOGGER.debug("[0x%04X] Configuring OppleCluster for feeder", nwk)
                
                # Initialize attributes
                opple_cluster._initialize_attributes()
                
                try:
                    import asyncio
                    await asyncio.sleep(1.0)  # Wait for initialization
                    await opple_cluster.read_attributes([FEEDER_ATTR], allow_cache=False)
                    LOGGER.debug("[0x%04X] Read initial device state", nwk)
                except Exception as e:
                    LOGGER.debug("[0x%04X] Could not read device state: %s", nwk, e)
                
                LOGGER.info("[0x%04X] Feeder configuration completed successfully", nwk)
        except Exception as e:
            nwk = getattr(self, 'nwk', 0)
            LOGGER.error("[0x%04X] Error during feeder configuration: %s", nwk, str(e))