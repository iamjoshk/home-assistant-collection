from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, PowerConfiguration
from zigpy.zcl.clusters.measurement import RelativeHumidity, TemperatureMeasurement
from zigpy.quirks import CustomCluster
from zigpy.quirks import CustomDevice
import logging

_LOGGER = logging.getLogger(__name__)

class SoilMoistureCluster(CustomCluster, RelativeHumidity):
    """Custom Soil Moisture cluster"""
    cluster_id = 0x0405
    ep_attribute = 'moisture'
    
    def _update_attribute(self, attrid, value):
        """Handle attribute updates."""
        _LOGGER.debug(f"Moisture update - ID: {attrid}, Value: {value}")
        super()._update_attribute(attrid, value)

class SoilTemperatureCluster(CustomCluster, TemperatureMeasurement):
    """Custom Soil Temperature cluster"""
    cluster_id = 0x0402
    ep_attribute = 'soil_temperature'
    
    def _update_attribute(self, attrid, value):
        """Handle attribute updates."""
        _LOGGER.debug(f"Temperature update - ID: {attrid}, Value: {value}")
        super()._update_attribute(attrid, value)

class ThirdRealitySoilMoisture(CustomDevice):
    """Third Reality Soil Moisture sensor"""

    signature = {
        "models_info": [
            ("Third Reality, Inc", "3RSM0147Z")
        ],
        "endpoints": {
            1: {
                "profile_id": zha.PROFILE_ID,
                "device_type": 0x0302,
                "input_clusters": [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    TemperatureMeasurement.cluster_id,
                    RelativeHumidity.cluster_id,
                    0xff01,
                ],
                "output_clusters": [0x0019]
            }
        }
    }

    replacement = {
        "endpoints": {
            1: {
                "profile_id": zha.PROFILE_ID,
                "device_type": 0x0302,
                "input_clusters": [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    SoilTemperatureCluster,
                    SoilMoistureCluster,
                    0xff01
                ],
                "output_clusters": [0x0019]
            }
        }
    }

    def __init__(self, *args, **kwargs):
        """Initialize device."""
        _LOGGER.debug("Initializing Third Reality Soil Moisture sensor")
        super().__init__(*args, **kwargs)

    async def configure(self):
        """Configure the device."""
        _LOGGER.debug("Starting Third Reality Soil Moisture sensor configuration")
        try:
            await super().configure()
            _LOGGER.debug("Configuring temperature cluster")
            temp_cluster = self.endpoints[1].in_clusters[SoilTemperatureCluster.cluster_id]
            if temp_cluster:
                await temp_cluster.bind()
                await temp_cluster.configure_reporting(0x0000, 300, 3600, 100)
                _LOGGER.debug("Temperature cluster configured")

            _LOGGER.debug("Configuring moisture cluster")
            moisture_cluster = self.endpoints[1].in_clusters[SoilMoistureCluster.cluster_id]
            if moisture_cluster:
                await moisture_cluster.bind()
                await moisture_cluster.configure_reporting(0x0000, 300, 3600, 100)
                _LOGGER.debug("Moisture cluster configured")
        except Exception as e:
            _LOGGER.error("Error during configuration: %s", str(e))
            raise
