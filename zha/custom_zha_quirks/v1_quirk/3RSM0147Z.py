"""Third Reality 3RSM0147Z soil moisture and temperature sensor."""
from typing import Final, Union

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

    MEASURED_VALUE_ATTR: Final = 0x0000
    MIN_MEASURED_VALUE_ATTR: Final = 0x0001
    MAX_MEASURED_VALUE_ATTR: Final = 0x0002

    attributes = {
        MEASURED_VALUE_ATTR: ('measured_value', t.uint16_t),
        MIN_MEASURED_VALUE_ATTR: ('min_measured_value', t.uint16_t),
        MAX_MEASURED_VALUE_ATTR: ('max_measured_value', t.uint16_t),
    }

    def _update_attribute(self, attrid: int, value: Union[int, float]) -> None:
        """Handle attribute updates."""
        _LOGGER.debug(f"Soil Moisture update - Attribute: {attrid}, Value: {value}")
        if attrid == self.MEASURED_VALUE_ATTR:
            # Convert the raw value to a percentage (0-100)
            if isinstance(value, (int, float)):
                # Ensure value is between 0 and 10000 (0% to 100%)
                value = min(10000, max(0, int(value)))
                super()._update_attribute(attrid, value)
                _LOGGER.debug(f"Soil Moisture processed value: {value/100}%")
        else:
            super()._update_attribute(attrid, value)

class TemperatureMeasurementCluster(CustomCluster, TemperatureMeasurement):
    """Temperature measurement cluster."""
    cluster_id = TemperatureMeasurement.cluster_id
    name = 'Temperature Measurement'
    ep_attribute = 'temperature'
    
    def _update_attribute(self, attrid: int, value: Union[int, float]) -> None:
        """Handle attribute updates."""
        _LOGGER.debug(f"Temperature update - ID: {attrid}, Value: {value}")
        super()._update_attribute(attrid, value)

class ThirdRealitySoilMoisture(CustomDevice):
    """Third Reality Soil Moisture sensor."""

    signature = {
        "endpoints": {
            1: {
                "profile_id": zha.PROFILE_ID,
                "device_type": zha.DeviceType.TEMPERATURE_SENSOR,
                "input_clusters": [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    TemperatureMeasurement.cluster_id,
                    RelativeHumidity.cluster_id,
                    0xff01,
                ],
                "output_clusters": [0x0019]
            }
        },
        "manufacturer": "Third Reality, Inc",
        "model": "3RSM0147Z",
    }

    replacement = {
        "endpoints": {
            1: {
                "device_type": zha.DeviceType.TEMPERATURE_SENSOR,
                "input_clusters": [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    TemperatureMeasurementCluster,
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
            
            _LOGGER.debug("Configuring temperature cluster")
            temp_cluster = self.endpoints[1].temperature
            if temp_cluster:
                await temp_cluster.bind()
                await temp_cluster.configure_reporting(
                    self.endpoints[1].temperature.MEASURED_VALUE_ATTR,
                    min_interval=300,    # 5 minutes
                    max_interval=3600,   # 1 hour
                    reportable_change=100
                )
                _LOGGER.debug("Temperature cluster configured successfully")

            _LOGGER.debug("Configuring soil moisture cluster")
            moisture_cluster = self.endpoints[1].soil_moisture
            if moisture_cluster:
                await moisture_cluster.bind()
                await moisture_cluster.configure_reporting(
                    moisture_cluster.MEASURED_VALUE_ATTR,
                    min_interval=300,    # 5 minutes
                    max_interval=3600,   # 1 hour
                    reportable_change=100  # 1% change
                )
                # Initialize min/max values
                await moisture_cluster._write_attributes({
                    moisture_cluster.MIN_MEASURED_VALUE_ATTR: 0,
                    moisture_cluster.MAX_MEASURED_VALUE_ATTR: 10000
                })
                _LOGGER.debug("Soil moisture cluster configured successfully")

        except Exception as e:
            _LOGGER.error("Error during configuration: %s", str(e))
            raise
