from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, PowerConfiguration
from zigpy.zcl.clusters.measurement import RelativeHumidity, TemperatureMeasurement
from zigpy.quirks import CustomCluster
from zigpy.quirks import CustomDevice

class SoilMoistureCluster(CustomCluster, RelativeHumidity):
    cluster_id = RelativeHumidity.cluster_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_attribute(0x0000, 'soil_moisture')

class ThirdRealitySoilMoisture(CustomDevice):
    signature = {
        "models_info": [
            ("Third Reality, Inc", "3RSM0147Z")
        ],
        "endpoints": {
            1: {
                "profile_id": zha.PROFILE_ID,
                "device_type": zha.DeviceType.HUMIDITY_SENSOR,
                "input_clusters": [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    TemperatureMeasurement.cluster_id,
                    RelativeHumidity.cluster_id,
                    0xff01  # Custom cluster ID
                ],
                "output_clusters": [
                    0x0019
                ]
            }
        }
    }
    replacement = {
        "endpoints": {
            1: {
                "profile_id": zha.PROFILE_ID,
                "device_type": zha.DeviceType.HUMIDITY_SENSOR,
                "input_clusters": [
                    SoilMoistureCluster,
                    PowerConfiguration.cluster_id,
                    TemperatureMeasurement.cluster_id,
                    Basic.cluster_id,
                    0xff01  # Custom cluster ID
                ],
                "output_clusters": [
                    0x0019
                ]
            }
        }
    }
