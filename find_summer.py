import argparse
import json
from summer_finder import find_summer_days, load_config, send_sms_notification

# This code uses Open-Meteo's weather forecasting API to determine which campgrounds near
# home are likely to have summer-like weekend temperatures within the next few weeks

# Set up argument parsing
parser = argparse.ArgumentParser(description="Find upcoming summer-like weekends at campgrounds near home.")
parser.add_argument('--input_file', type=str, default='all-campgrounds.json', help='Input file containing the list of campgrounds.')
parser.add_argument('--config_file', type=str, default='config.json', help='Config file containing phone, home_lat, and home_long values.')
parser.add_argument('--max_miles', type=float, default=400, help='Maximum distance from home in miles.')
parser.add_argument('--min_high_temp', type=float, default=70, help='Minimum high temperature for a nice summer day (Fahrenheit).')
parser.add_argument('--max_high_temp', type=float, default=88, help='Maximum high temperature for a nice summer day (Fahrenheit).')
parser.add_argument('--prefer_waterfront', action='store_true', help='Prefer waterfront campgrounds in results.')
parser.add_argument('--all_days', action='store_true', help='Include all days of the week, not just weekends.')
args = parser.parse_args()

MAX_MILES = args.max_miles
MIN_HIGH_TEMP = args.min_high_temp
MAX_HIGH_TEMP = args.max_high_temp

config = load_config(args.config_file)
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

def progress_callback(message):
    """Print progress messages to console."""
    print(message)

# Find summer days using shared core functionality
summer_days = find_summer_days(
    max_miles=MAX_MILES,
    min_high_temp=MIN_HIGH_TEMP,
    max_high_temp=MAX_HIGH_TEMP,
    home_lat=home_lat,
    home_long=home_long,
    config_file=args.config_file,
    input_file=args.input_file,
    progress_callback=progress_callback,
    prefer_waterfront=args.prefer_waterfront,
    weekends_only=not args.all_days
)

if summer_days:
    with open("sorted_summer_days.json", "wt") as f:
        f.write(json.dumps(summer_days, indent=2))
    
    if phone:
        resp = send_sms_notification(phone, json.dumps(summer_days[0]))
        print(resp.json())
else:
    print("No summer days found :(")
