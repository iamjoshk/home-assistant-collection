"""Third Reality 3RSM0147Z soil moisture and temperature sensor."""
from zigpy.quirks.v2 import QuirkBuilder
from zigpy.quirks.v2.homeassistant import EntityType, EntityPlatform, PERCENTAGE
from zigpy.quirks.v2.homeassistant.number import NumberDeviceClass
from zigpy.zcl.clusters.measurement import RelativeHumidity
from zigpy.zcl.clusters.general import Basic

(
    QuirkBuilder("Third Reality, Inc", "3RSM0147Z")
    .replaces(RelativeHumidity)
    .number(
        RelativeHumidity.AttributeDefs.measured_value.name,
        RelativeHumidity.cluster_id,
        multiplier=0.01,
        device_class=NumberDeviceClass.MOISTURE,
        min_value=0,
        max_value=100,
        unit=PERCENTAGE,
        translation_key="moisture",
        fallback_name="Soil Moisture"
    )
    .add_to_registry()
)


