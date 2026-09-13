"""Coordinate and geospatial utility helpers.

NOTE: This module provides a synthetic/coarse prototype coastline mask suitable for
the current synthetic scientific simulation prototype. It is NOT an operational-grade
hydrographic or navigation chart dataset.
"""

import math
from typing import Tuple

from shapely.geometry import Point, Polygon
from shapely.prepared import prep

EARTH_RADIUS_KM = 6371.0088

# Refined synthetic coastline polygon representing major Antarctic sectors:
# Antarctic Peninsula, Weddell Sea, Queen Maud Land, Enderby Land, Prydz Bay,
# Wilkes Land, Ross Sea, and Marie Byrd Land.
# Clearly marked as a synthetic prototype boundary.
SYNTHETIC_COASTLINE = (
    (-180.0, -78.0), (-170.0, -78.0), (-160.0, -78.0), (-150.0, -76.0),
    (-140.0, -74.0), (-130.0, -74.0), (-120.0, -73.5), (-110.0, -73.0),
    (-100.0, -72.5), (-90.0, -72.0), (-80.0, -73.0), (-75.0, -70.0),
    (-70.0, -68.0), (-65.0, -65.0), (-63.0, -63.5), (-57.0, -63.5),
    (-55.0, -65.0), (-60.0, -72.0), (-55.0, -75.0), (-45.0, -76.0),
    (-35.0, -76.0), (-25.0, -75.0), (-15.0, -72.0), (-5.0, -70.5),
    (0.0, -70.0), (10.0, -70.0), (15.0, -70.0), (20.0, -69.8),
    (30.0, -69.5), (40.0, -69.0), (45.0, -67.5), (50.0, -66.5),
    (55.0, -66.5), (65.0, -67.5), (70.0, -69.0), (74.0, -69.5),
    (76.0, -69.6), (78.0, -69.6), (79.0, -69.6), (80.0, -68.5),
    (85.0, -67.0), (90.0, -66.5), (100.0, -66.0), (110.0, -66.0),
    (120.0, -66.0), (130.0, -66.0), (140.0, -66.5), (150.0, -67.0),
    (155.0, -68.0), (160.0, -70.0), (165.0, -72.5), (170.0, -76.0),
    (175.0, -78.0), (180.0, -78.0),
)
SYNTHETIC_ANTARCTIC_LAND = Polygon(SYNTHETIC_COASTLINE + ((180.0, -90.0), (-180.0, -90.0)))


class SyntheticAntarcticMask:
    """Deterministic coarse land mask for the synthetic prototype."""

    model_version = "synthetic-coastline-2"

    def __init__(self, polygon: Polygon = SYNTHETIC_ANTARCTIC_LAND):
        self.polygon = polygon
        self.prepared = prep(polygon)
        self._exterior = polygon.exterior

    def is_ocean(self, latitude: float, longitude: float, length_m: float = 0.0, width_m: float = 0.0, buffer_m: float = 500.0) -> bool:
        latitude = float(latitude)
        longitude = float(longitude)
        if not -90.0 <= latitude <= 90.0 or not -180.0 <= longitude <= 180.0:
            return False
        point = Point(longitude, latitude)
        if self.prepared.contains(point) or self.polygon.intersects(point):
            return False
        footprint_radius_m = math.hypot(max(0.0, float(length_m)), max(0.0, float(width_m))) / 2.0 + max(0.0, float(buffer_m))
        if footprint_radius_m <= 0.0:
            return True
        latitude_radius = footprint_radius_m / 111000.0
        longitude_radius = footprint_radius_m / max(111000.0 * math.cos(math.radians(latitude)), 1.0)
        radius = max(latitude_radius, longitude_radius)
        footprint = point.buffer(radius, resolution=8)
        return not self.prepared.intersects(footprint)

    def distance_to_land_km(self, latitude: float, longitude: float) -> float:
        """Estimate distance from a point to the nearest land boundary in km."""
        latitude = float(latitude)
        longitude = float(longitude)
        point = Point(longitude, latitude)
        if self.prepared.contains(point) or self.polygon.intersects(point):
            return 0.0
        deg_dist = self._exterior.distance(point)
        lat_cos = max(0.2, math.cos(math.radians(latitude)))
        metric_scale = 111.0 * math.sqrt(0.5 * (1.0 + lat_cos * lat_cos))
        return round(float(deg_dist * metric_scale), 2)

    def nearest_ocean_position(self, latitude: float, longitude: float, length_m: float = 0.0, width_m: float = 0.0, buffer_m: float = 500.0) -> Tuple[float, float]:
        """Find the nearest ocean position guaranteed to satisfy the footprint safety check."""
        latitude = float(latitude)
        longitude = float(longitude)
        if self.is_ocean(latitude, longitude, length_m, width_m, buffer_m):
            return latitude, longitude
        test_lat = latitude
        for _ in range(240):
            test_lat += 0.05
            if test_lat > -50.0:
                break
            if self.is_ocean(test_lat, longitude, length_m, width_m, buffer_m) and self.is_ocean(test_lat + 0.02, longitude, length_m, width_m, buffer_m):
                return round(test_lat + 0.02, 5), round(longitude, 5)
        for r_deg in (0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0):
            for angle in (0.0, 0.3927, 0.7854, 1.1781, 1.5708, 1.9635, 2.3562, 2.7489, 3.1416, 3.5343, 3.9270, 4.3197, 4.7124, 5.1051, 5.4978, 5.8905):
                plat = latitude + r_deg * math.cos(angle)
                plon = longitude + r_deg * math.sin(angle)
                if -90.0 <= plat <= 90.0 and -180.0 <= plon <= 180.0:
                    if self.is_ocean(plat, plon, length_m, width_m, buffer_m):
                        return round(plat, 5), round(plon, 5)
        return round(latitude, 5), round(longitude, 5)


DEFAULT_ANTARCTIC_MASK = SyntheticAntarcticMask()


def is_ocean(latitude: float, longitude: float, length_m: float = 0.0, width_m: float = 0.0, buffer_m: float = 500.0) -> bool:
    return DEFAULT_ANTARCTIC_MASK.is_ocean(latitude, longitude, length_m, width_m, buffer_m)


def haversine_km(first_latitude: float, first_longitude: float, second_latitude: float, second_longitude: float) -> float:
    latitude_one = math.radians(first_latitude)
    latitude_two = math.radians(second_latitude)
    delta_latitude = math.radians(second_latitude - first_latitude)
    delta_longitude = math.radians(second_longitude - first_longitude)
    value = math.sin(delta_latitude / 2.0) ** 2 + math.cos(latitude_one) * math.cos(latitude_two) * math.sin(delta_longitude / 2.0) ** 2
    return EARTH_RADIUS_KM * 2.0 * math.atan2(math.sqrt(value), math.sqrt(max(0.0, 1.0 - value)))

