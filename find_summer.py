import requests
import json
from datetime import datetime
from geopy.distance import great_circle
import argparse
import os

# This code uses Open-Meteo's weather forecasting API to determine which campgrounds near
# home are likely to have summer-like weekend temperatures within the next few weeks

# Set up argument parsing
parser = argparse.ArgumentParser(description="Find upcoming summer-like weekends at campgrounds near home.")
parser.add_argument('--input_file', type=str, default='all-campgrounds.json', help='Input file containing the list of campgrounds.')
parser.add_argument('--config_file', type=str, default='config.json', help='Config file containing phone, home_lat, and home_long values.')
parser.add_argument('--max_miles', type=float, default=400, help='Maximum distance from home in miles.')
parser.add_argument('--min_high_temp', type=float, default=70, help='Minimum high temperature for a nice summer day (Fahrenheit).')
parser.add_argument('--max_high_temp', type=float, default=88, help='Maximum high temperature for a nice summer day (Fahrenheit).')
args = parser.parse_args()

MAX_MILES = args.max_miles
MIN_HIGH_TEMP = args.min_high_temp
MAX_HIGH_TEMP = args.max_high_temp

config = {}
if os.path.exists(args.config_file):
    with open(args.config_file, 'rt') as f:
        config = json.load(f)
home_lat = config.get("home_lat", None)
home_long = config.get("home_long", None)
phone = config.get("phone", None)

if home_lat and home_long:
    home = (home_lat, home_long)
    print(f"Considering campgrounds within {MAX_MILES} miles of home {home}.")
else:
    home = None
    print("Warning: No home location provided. All campgrounds will be considered.")

if phone:
    print(f"The best option, if found, will be sent via SMS to {phone}.")
else:
    print("No phone number provided.  SMS message will not be sent.")

def get_day_of_week(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day_name = date_obj.strftime('%A')
    return day_name

with open(args.input_file, "rt") as f:
    j = f.read()
    campgrounds = json.loads(j)

summer_days = []
for campground in campgrounds:
    name = campground["name"]
    print(f"Checking {name}")
    lat, long = campground["location"].split(",")
    point = (float(lat), float(long))
    dist = great_circle(home, point).miles if home else 0
    if dist >= MAX_MILES:
        continue
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=temperature_2m_max&timezone=auto&forecast_days=16&temperature_unit=fahrenheit"
    data = None
    while not data:
        try:
            response = requests.get(url, timeout=10)  # Timeout after 10 seconds
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            print("Request timed out")
        except requests.RequestException as e:
            print(f"Error: {e}")
    for index, temp in enumerate(data["daily"]["temperature_2m_max"]):
        if temp and temp >= MIN_HIGH_TEMP and temp <= MAX_HIGH_TEMP:
            date = data["daily"]["time"][index]
            day = get_day_of_week(date)
            if day in ["Saturday","Sunday"]:
                summer_day = {
                    "dist": dist,
                    "date": date,
                    "day": day,
                    "temp": temp,
                    "name": name
                }
                print(json.dumps(summer_day))
                summer_days.append(summer_day)
if summer_days:
    sorted_summer_days = sorted(summer_days, key=lambda d: d['dist'])
    with open("sorted_summer_days.json", "wt") as f:
        f.write(json.dumps(sorted_summer_days, indent=2))
    if phone:
        resp = requests.post('https://textbelt.com/text', {
            'phone': phone,
            'message': json.dumps(sorted_summer_days[0]),
            'key': 'textbelt',
        })
        print(resp.json())
else:
    print("No summer days found :(")
