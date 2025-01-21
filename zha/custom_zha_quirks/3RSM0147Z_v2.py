"""Third Reality 3RSM0147Z soil moisture and temperature sensor."""
from zigpy.quirks.v2 import QuirkBuilder
from zigpy.quirks.v2.homeassistant import EntityType, EntityPlatform
from zigpy.quirks.v2.homeassistant.sensor import SensorDeviceClass, SensorStateClass
from zigpy.zcl.clusters.measurement import RelativeHumidity
from zigpy.zcl.clusters.general import Basic

(
    QuirkBuilder("Third Reality, Inc", "3RSM0147Z")
#    .replaces(RelativeHumidity.cluster_id)
    .sensor(
        RelativeHumidity.AttributeDefs.measured_value.name,
        RelativeHumidity.cluster_id,
        multiplier=0.01,
        device_class=SensorDeviceClass.MOISTURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit="%"
        fallback_name="Soil Moisture"
    )
    .add_to_registry()
)


