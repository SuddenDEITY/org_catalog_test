"""Geolocation utilities."""


from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    """Calculate the distance between two coordinates using the Haversine formula."""

    lat_a_rad, lon_a_rad = radians(lat_a), radians(lon_a)
    lat_b_rad, lon_b_rad = radians(lat_b), radians(lon_b)

    d_lat = lat_b_rad - lat_a_rad
    d_lon = lon_b_rad - lon_a_rad

    sin_lat = sin(d_lat / 2)
    sin_lon = sin(d_lon / 2)

    a = sin_lat**2 + cos(lat_a_rad) * cos(lat_b_rad) * sin_lon**2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS_KM * c


def bounding_box(
    latitude: float,
    longitude: float,
    radius_km: float,
) -> tuple[float, float, float, float]:
    """Return latitude/longitude bounds covering the requested radius."""

    delta_lat = (radius_km / EARTH_RADIUS_KM) * (180 / 3.141592653589793)
    delta_lon = delta_lat / cos(radians(latitude)) if radius_km else 0

    return (
        latitude - delta_lat,
        latitude + delta_lat,
        longitude - delta_lon,
        longitude + delta_lon,
    )
