from zigpy.quirks.v2 import QuirkBuilder

from zigpy.zcl.clusters.general import (
    PowerConfiguration
)

from zigpy.device import Device
from zigpy.exceptions import MultipleQuirksMatchException
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice, signature_matches
from zigpy.quirks.registry import DeviceRegistry
from zigpy.quirks.v2 import (
    BinarySensorMetadata,
    CustomDeviceV2,
    EntityMetadata,
    EntityPlatform,
    EntityType,
    NumberMetadata,
    SwitchMetadata,
    WriteAttributeButtonMetadata,
    ZCLCommandButtonMetadata,
    ZCLSensorMetadata,
    add_to_registry_v2,
)
import zigpy.types as t
from zigpy.zcl import ClusterType
from zigpy.zcl.clusters.homeautomation import Diagnostic
from zigpy.zcl.foundation import BaseAttributeDefs, ZCLAttributeDef, ZCLCommandDef

from .async_mock import sentinel


(
  
  QuirkBuilder("Leedarson", "LDHD2AZW")
  .sensor(
    PowerConfiguration.AttributeDefs.battery_voltage.name,
    PowerConfiguration.cluster_id,
  )
  .skip_configuration()
  .add_to_registry()

)
