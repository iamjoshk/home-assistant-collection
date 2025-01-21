"""Third Reality 3RSM0147Z soil moisture and temperature sensor."""
from zigpy.quirks.v2 import QuirkBuilder
from zigpy.quirks.v2.homeassistant.sensor import SensorDeviceClass, SensorStateClass
from zigpy.quirks.v2.homeassistant import UnitOfMeasure
from zigpy.zcl.clusters.measurement import RelativeHumidity
from zigpy.zcl.clusters.general import Basic

(
    QuirkBuilder("Third Reality, Inc", "3RSM0147Z")
    .sensor(
        RelativeHumidity.cluster_id,
        RelativeHumidity.AttributeDefs.measured_value.id,
        device_class=SensorDeviceClass.MOISTURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit=UnitOfMeasure.PERCENT,
        fallback_name="Soil Moisture"
    )
    .add_to_registry()
)
