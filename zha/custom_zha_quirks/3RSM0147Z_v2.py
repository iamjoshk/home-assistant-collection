"""Third Reality 3RSM0147Z soil moisture and temperature sensor."""

from zigpy.quirks.v2 import QuirkBuilder

from zigpy.zcl.clusters.measurement import SoilMoisture

from zhaquirks import CustomCluster



class SoilMoistureCluster(SoilMoisture, CustomCluster):
    """Soil Moisture Cluster for TR"""
    
    cluster_id = 1029

(
    QuirkBuilder("Third Reality, Inc", "3RSM0147Z")
    .replaces(SoilMoistureCluster, 1029, endpoint_id=1)
    .add_to_registry()
)

