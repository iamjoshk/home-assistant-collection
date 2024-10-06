from zigpy.quirks.v2 import QuirkBuilder

from zigpy.zcl.clusters.general import (
    PowerConfiguration
)
from zigpy.quirks.v2 import (
    add_to_registry_v2,
)



(
  
  QuirkBuilder("Leedarson", "LDHD2AZW")
  .sensor(
    PowerConfiguration.AttributeDefs.battery_voltage.name,
    PowerConfiguration.cluster_id,
  )
  .skip_configuration()
  .add_to_registry()

)
