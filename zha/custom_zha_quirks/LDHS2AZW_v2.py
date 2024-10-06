from zigpy.quirks.v2 import QuirkBuilder

from zigpy.zcl.clusters.general import (
    PowerConfiguration
)


(
  
  QuirkBuilder("Leedarson", "LDHD2AZW")
  .number(
    PowerConfiguration.AttributeDefs.battery_voltage.name,
    PowerConfiguration.cluster_id,
    min_value=0,
    max_value=100,
    step=1,
    unit="v",
  )
  .skip_configuration()
  .add_to_registry()

)
