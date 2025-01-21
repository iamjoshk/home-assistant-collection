"""Third Reality 3RSM0147Z soil moisture and temperature sensor."""
from zigpy.quirks.v2 import QuirkBuilder
from zigpy.zcl.clusters.measurement import RelativeHumidity
from zigpy.zcl.clusters.general import Basic

(
    QuirkBuilder("Third Reality, Inc","3RSM0147Z")
    .adds(RelativeHumidity)
    .sensor(
        RelativeHumidity.cluster_id,
        RelativeHumidity.AttributeDefs.measured_value.name,
        device_class="SensorDeviceClass.MOISTURE",
        state_class="SensorDeviceClass.MOISTURE",
        unit="%",
        fallback_name="Soil Moisture"
    )
    .add_to_registry()
)
