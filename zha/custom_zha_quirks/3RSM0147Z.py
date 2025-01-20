"""Third Reality 3RSM0147Z soil moisture and temperature sensor."""
from typing import Final

from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, PowerConfiguration
from zigpy.zcl.clusters.measurement import RelativeHumidity, TemperatureMeasurement
from zigpy.quirks import CustomCluster, CustomDevice
from zigpy.zcl import foundation
import zigpy.types as t
import logging

_LOGGER = logging.getLogger(__name__)

class SoilMoistureCluster(CustomCluster, RelativeHumidity):
    """Custom Soil Moisture cluster."""
    cluster_id = RelativeHumidity.cluster_id
    name = 'Soil Moisture Measurement'
    ep_attribute = 'soil_moisture'
    
    def _update_attribute(self, attrid, value):
        """Handle attribute updates."""
        _LOGGER.debug(f"Soil Moisture update - ID: {attrid}, Value: {value}")
        super()._update_attribute(attrid, value)

class TemperatureMeasurementClusterSoil(CustomCluster, TemperatureMeasurement):
    """Custom Temperature Measurement cluster."""
    cluster_id = TemperatureMeasurement.cluster_id
    name = 'Temperature Measurement'
    ep_attribute = 'temperature'  # Changed from 'soil_temperature' to match HA expectations
    
    def _update_attribute(self, attrid, value):
        """Handle attribute updates."""
        _LOGGER.debug(f"Temperature update - ID: {attrid}, Value: {value}")
        super()._update_attribute(attrid, value)

class ThirdRealitySoilMoisture(CustomDevice):
    """Third Reality Soil Moisture sensor."""

    signature = {
        "models_info": [
            ("Third Reality, Inc", "3RSM0147Z")
        ],
        "endpoints": {
            1: {
                "profile_id": zha.PROFILE_ID,
                "device_type": zha.DeviceType.TEMPERATURE_SENSOR,  # Using standard temperature sensor type
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
                "device_type": zha.DeviceType.TEMPERATURE_SENSOR,
                "input_clusters": [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    TemperatureMeasurementClusterSoil,  # Updated class name
                    SoilMoistureCluster,
                ],
                "output_clusters": [0x0019]
            }
        }
    }

    async def configure(self):
        """Configure the device."""
        _LOGGER.debug("Starting Third Reality Soil Moisture sensor configuration")
        try:
            await super().configure()
            
            # Configure temperature reporting
            temperature_cluster = self.endpoints[1].temperature  # Updated to match ep_attribute
            if temperature_cluster:
                _LOGGER.debug("Binding temperature cluster")
                await temperature_cluster.bind()
                _LOGGER.debug("Configuring temperature reporting")
                await temperature_cluster.configure_reporting(
                    0x0000,              # Measured value attribute ID
                    min_interval=300,    # 5 minutes
                    max_interval=3600,   # 1 hour
                    reportable_change=100
                )
                _LOGGER.debug("Temperature cluster configured successfully")

            # Configure soil moisture reporting
            moisture_cluster = self.endpoints[1].soil_moisture
            if moisture_cluster:
                _LOGGER.debug("Binding soil moisture cluster")
                await moisture_cluster.bind()
                _LOGGER.debug("Configuring soil moisture reporting")
                await moisture_cluster.configure_reporting(
                    0x0000,              # Measured value attribute ID
                    min_interval=300,    # 5 minutes
                    max_interval=3600,   # 1 hour
                    reportable_change=100
                )
                _LOGGER.debug("Soil moisture cluster configured successfully")

        except Exception as e:
            _LOGGER.error("Error during configuration: %s", str(e))
            raise
