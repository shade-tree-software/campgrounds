import sys
import requests

# Look up the elevation (in meters) for a single latitude/longitude using
# the open-elevation API.
#
# Usage: python get_elevation.py <latitude> <longitude>
# Example: python get_elevation.py 38.2474 -78.6704

def get_elevation(latitude: float, longitude: float) -> float:
    """Return elevation in meters for the given coordinates."""
    url = "https://api.open-elevation.com/api/v1/lookup"
    params = {"locations": f"{latitude},{longitude}"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["results"][0]["elevation"]


if __name__ == "__main__":
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    print(get_elevation(lat, lon))
