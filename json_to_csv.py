import json
import sys

import pandas as pd

# Converts campground JSON data to a Google My Maps-compatible CSV.
#
# Input JSON format:
# [
#   {
#     "name": "FR 812 Dispersed Sites",
#     "location": "37.6103,-79.3787",
#     "elevation_meters": 269,
#     "note": "https://thedyrt.com/..."
#   },
#   ...
# ]
#
# The output adds computed fields: elevation_feet, delta_temp (temperature
# difference in °F relative to BASE_LOCATION, based on latitude and altitude),
# climate (categorical label derived from delta_temp), and visited (yes/no
# derived from presence of a "stays" field in the input).

BASE_LOCATION = {
    "name": "Reston, VA",
    "latitude": 38.9527,
    "longitude": -77.3412,
    "altitude_meters": 110,
}

METERS_TO_FEET = 3.281
CELSIUS_PER_DEGREE_LATITUDE = -1.0
CELSIUS_PER_METER_ALTITUDE = -0.0065
CELSIUS_TO_FAHRENHEIT = 9.0 / 5.0

# Fields from the input JSON that should not appear in the output CSV.
EXCLUDED_FIELDS = {"index", "stays", "elevation_meters"}


def cooling_effect_fahrenheit(latitude: float, altitude_meters: float) -> float:
    """Temperature difference (°F) of a location relative to BASE_LOCATION."""
    delta_lat = latitude - BASE_LOCATION["latitude"]
    delta_alt = altitude_meters - BASE_LOCATION["altitude_meters"]
    delta_celsius = (CELSIUS_PER_DEGREE_LATITUDE * delta_lat
                     + CELSIUS_PER_METER_ALTITUDE * delta_alt)
    return delta_celsius * CELSIUS_TO_FAHRENHEIT


def classify_climate(delta_temp: float) -> str:
    """Return a climate label based on the temperature differential (°F)."""
    if delta_temp <= -14.0:
        return "much cooler"
    if delta_temp <= -9.0:
        return "cooler"
    if delta_temp <= -4.0:
        return "slightly cooler"
    if delta_temp <= 4.0:
        return "similar"
    if delta_temp < 9.0:
        return "slightly warmer"
    if delta_temp < 14.0:
        return "warmer"
    if delta_temp < 19.0:
        return "much warmer"
    return "hot"


def process_campground(entry: dict) -> dict | None:
    """Transform a campground JSON entry into a My Maps-compatible CSV row."""
    location = entry.get("location")
    if location is None:
        return None

    lat, lon = (float(x) for x in location.split(","))
    elev_meters = entry.get("elevation_meters", 0)
    delta_temp = cooling_effect_fahrenheit(lat, elev_meters)

    row = {k: v for k, v in entry.items() if k not in EXCLUDED_FIELDS}
    row["elevation_feet"] = int(elev_meters * METERS_TO_FEET)
    row["delta_temp"] = delta_temp
    row["climate"] = classify_climate(delta_temp)
    row["visited"] = "yes" if "stays" in entry else "no"

    return row


def main():
    input_filename = sys.argv[1] if len(sys.argv) > 1 else "all-campgrounds.json"
    output_filename = sys.argv[2] if len(sys.argv) > 2 else "all-campgrounds.csv"

    with open(input_filename) as f:
        input_data = json.load(f)

    rows = []
    for entry in input_data:
        row = process_campground(entry)
        if row is not None:
            rows.append(row)

    pd.DataFrame(rows).to_csv(output_filename, index=False)


if __name__ == "__main__":
    main()
