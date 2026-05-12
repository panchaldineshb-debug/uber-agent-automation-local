from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Approximate bounding box for Edison, NJ
_EDISON_BOUNDS = {
    "lat_min": 40.47, "lat_max": 40.59,
    "lon_min": -74.45, "lon_max": -74.28,
}

_geolocator = Nominatim(user_agent="sarabilabs_uber_agent")


def get_coordinates(address: str) -> tuple[float, float]:
    try:
        location = _geolocator.geocode(address)
        if not location:
            raise ValueError(f"Address not found: {address!r}")
        return (location.latitude, location.longitude)
    except GeocoderTimedOut:
        return get_coordinates(address)


def validate_edison_nj(address: str) -> bool:
    try:
        lat, lon = get_coordinates(address)
        b = _EDISON_BOUNDS
        return b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]
    except Exception:
        return False
