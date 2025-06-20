import pandas as pd
import json
import sys

# This is the main processing code for generating Google Maps friendly CSV files
# from the standard campgrounds JSON list data.  The campgrounds JSON list data
# should be in the following format:
#
# [
#  {
#    "name": "FR 812 Dispersed Sites",
#    "location": "37.6103,-79.3787",
#    "elevation": 269,
#    "note": "https://thedyrt.com/press/2025-best-places-to-camp-in-the-southeast-region/"
#  },
#  {
#    "name": "Meriwether Lewis Campground",
#    "location": "35.5232,-87.4570",
#    "elevation": 260,
#    "note": "https://thedyrt.com/press/2025-best-places-to-camp-in-the-southeast-region/"
#  },
#  ...
# ]
#
# Note that the elevation should be in meters.  This value is important and is
# used to calculate the temperature differential which is included in the output
# CSV file along with the elevation converted to feet.  The temperature 
# differential is calculated from the base location indicated by BASE_LOC.
# Note that the format of BASE_LOC is different, with separate float values for
# latitude and longitude, and the elevation value is called altitude_meters
# instead of elevation to reduce possible ambiguities in human understanding of
# the math formulas.
#

meters_2_feet = lambda x: x * 3.281
celsius_change_latitude = lambda x: -1.0 * x
celsius_change_altitude = lambda x: -0.0065 * x
BASE_LOC = {
        "name": "Reston, VA",
        "latitude": 38.9527,
        "longitude": -77.3412,
        "altitude_meters": 110
    }

def cooling_effect(latitude: float, altitude_meters: float) -> float:
    delta_latitude = latitude - BASE_LOC["latitude"]
    delta_altitude_meters = altitude_meters - BASE_LOC["altitude_meters"]
    delta_celsius_latitude = celsius_change_latitude(delta_latitude)
    delta_celsius_altitude = celsius_change_altitude(delta_altitude_meters)
    return delta_celsius_latitude + delta_celsius_altitude

input_filename = sys.argv[1]
output_filename = sys.argv[2]

with open(input_filename, "rt") as f:
    input_data = json.loads(f.read())

df = pd.DataFrame(columns=["location","name","note","elevation","delta_temp"])

for elem in input_data:
    loc = elem.get("location")
    lat,lon = list(map(lambda x: float(x), loc.split(",")))
    elev_meters = elem.get("elevation",0)
    elev_feet = meters_2_feet(elev_meters)
    elev = int(elev_feet)
    delta_celsius = cooling_effect(lat, elev_meters)
    delta_fahrenheit = delta_celsius * (9.0 / 5.0)
    if loc is not None:
        df.loc[len(df)] = pd.Series({"location":loc,"name":elem.get("name",""),"note":elem.get("note",""),"elevation":elev,"delta_temp":delta_fahrenheit})

df.to_csv(output_filename, index=False)
