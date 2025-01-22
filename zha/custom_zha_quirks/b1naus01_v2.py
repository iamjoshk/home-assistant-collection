"""Xiaomi aqara single rocker switch devices."""

import copy
from enum import Enum

from zigpy.types import t

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

from zhaquirks import Bus, EventableCluster
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
    DEVICE_TYPE,
    DOUBLE_PRESS,
    ENDPOINT_ID,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    SHORT_PRESS,
    SKIP_CONFIGURATION,
    VALUE,
)
from zhaquirks.xiaomi import (
    LUMI,
    AnalogInputCluster,
    BasicCluster,
    DeviceTemperatureCluster,
    ElectricalMeasurementCluster,
    MeteringCluster,
    OnOffCluster,
    XiaomiCustomDevice,
)

from zhaquirks.xiaomi.aqara.opple_remote import MultistateInputCluster, OppleCluster


class OppleOperationMode(t.uint8_t, Enum):
    """Opple operation_mode enum."""

    Decoupled = 0x00
    Coupled = 0x01
    

class OppleSwitchMode(t.uint8_t, Enum):
    """Opple switch_mode enum."""

    Fast = 0x01
    Multi = 0x02


class OppleSwitchType(t.uint8_t, Enum):
    """Opple switch_type enum."""

    Toggle = 0x01
    Momentary = 0x02


class OppleIndicatorLight(t.uint8_t, Enum):
    """Opple indicator light enum."""

    Normal = 0x00
    Reverse = 0x01


class OppleSwitchCluster(OppleCluster, EventableCluster):
    """Xiaomi mfg cluster implementation."""

    attributes = copy.deepcopy(OppleCluster.attributes)
    attributes.update(
        {
            0x0002: ("power_outage_count", t.uint8_t, True),
            0x000A: ("switch_type", OppleSwitchType, True),
            0x00F0: ("reverse_indicator_light", OppleIndicatorLight, True),
            0x0125: ("switch_mode", OppleSwitchMode, True),
            0x0200: ("operation_mode", OppleOperationMode, True),
            0x0201: ("power_outage_memory", t.Bool, True),
            0x0202: ("auto_off", t.Bool, True),
            0x0203: ("do_not_disturb", t.Bool, True),
            0x0000: ('toggle_operation_mode', OppleOperationMode, True),
            
        }
    )

    def __init__(self, *args, **kwargs):
        """Init."""
        self.power_bus = Bus()
        super().__init__(*args, **kwargs)


   
    async def toggle_operation_mode(self):
        """Toggle the operation mode between coupled and decoupled."""
        result = await self.read_attributes(['operation_mode'])
        success, _failure = result
        if success and 'operation_mode' in success:
            current_mode = success['operation_mode']
            new_mode = 0 if current_mode == 1 else 1
            await self.write_attributes({'operation_mode': new_mode})
            
        
class b1naus01(XiaomiCustomDevice):
    """Aqara single gang switch device."""

    class WallSwitchMultistateInputCluster(EventableCluster, MultistateInput):
        """WallSwitchMultistateInputCluster: fire events corresponding to press type."""

    def __init__(self, *args, **kwargs):
        """Init."""
        self.power_bus = Bus()
        super().__init__(*args, **kwargs)
        

class EventableOnOffCluster(EventableCluster, OnOffCluster):
    
    def __init__(self, *args, **kwargs):
        """Init."""
        self.power_bus = Bus()
        super().__init__(*args, **kwargs)
    
(
    QuirkBuilder("LUMI", "lumi.switch.b1naus01")
    .adds(OppleSwitchCluster, endpoint_id=1)
    .adds(b1naus01.WallSwitchMultistateInputCluster, endpoint_id=1)
    .adds(EventableOnOffCluster, endpoint_id=1)
    .binary_sensor(
        OppleSwitchCluster.AttributeDefs.operation_mode.name,
        OppleSwitchCluster.cluster_id,
        translation_key="couple_mode",
        fallback_name="Coupled Mode"
     )
    .command_button(
        command_name="toggle_operation_mode",
        cluster_id=OppleSwitchCluster.cluster_id,
        translation_key="toggle_operation_mode",
        fallback_name="Toggle Operation Mode"
    )
    .add_to_registry()
)
