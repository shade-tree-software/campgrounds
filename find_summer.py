"""CLI front end for the forecast search (weather_finder.py).

The web front end for this now lives inside EKKO Trips as the admin-only
Weather Finder page (/campgrounds/weather); the standalone summer_seeker_app.py
that used to serve it is gone. This script stays as the scriptable path — it's
the one that can text you the answer.
"""

import argparse
import json

import weather_finder as wf

parser = argparse.ArgumentParser(
    description="Find upcoming days with the weather you want at campgrounds near home.")
parser.add_argument('--input_file', default='campgrounds.json',
                    help='Campground database to search.')
parser.add_argument('--config_file', default='home.json',
                    help='Config file containing phone, home_lat, and home_long.')
parser.add_argument('--mode', choices=wf.MODES, default=wf.MODE_RANGE,
                    help='range: an absolute comfort band. cooler/warmer: relative to '
                         'home on the same day.')
parser.add_argument('--max_miles', type=float, default=250,
                    help='Maximum distance from home in miles.')
parser.add_argument('--min_high_temp', type=float, default=70,
                    help='[range mode] Minimum high temperature (F).')
parser.add_argument('--max_high_temp', type=float, default=88,
                    help='[range mode] Maximum high temperature (F).')
parser.add_argument('--delta_f', type=float, default=5,
                    help='[cooler/warmer mode] Minimum difference from home (F).')
parser.add_argument('--max_precip', type=float, default=None,
                    help='Only days with at most this much rain (inches).')
parser.add_argument('--waterfront_only', action='store_true',
                    help='Only campgrounds with a water designation (views included).')
parser.add_argument('--sort', choices=wf.SORTS, default='distance',
                    help='Order results by distance, temp, rain, or waterfront.')
parser.add_argument('--all_days', action='store_true',
                    help='Include every day, not just weekends.')
parser.add_argument('--output', default='sorted_summer_days.json',
                    help='Where to write the full result.')
args = parser.parse_args()

config = wf.load_config(args.config_file)
home_lat, home_long = config.get("home_lat"), config.get("home_long")
phone = config.get("phone")
if home_lat is None or home_long is None:
    raise SystemExit(f"{args.config_file} has no home_lat/home_long — nothing to search from.")

print(f"Considering campgrounds within {args.max_miles} miles of home.")
if phone:
    print(f"The best option, if found, will be sent via SMS to {phone}.")

try:
    result = wf.find_matching_days(
        wf.load_campgrounds(args.input_file), (home_lat, home_long),
        mode=args.mode,
        min_high=args.min_high_temp, max_high=args.max_high_temp, delta_f=args.delta_f,
        max_miles=args.max_miles, weekends_only=not args.all_days,
        max_precip_in=args.max_precip, waterfront_only=args.waterfront_only,
        sort=args.sort,
        progress=lambda done, total: print(f"  fetched {done}/{total} forecast points"),
    )
except wf.RateLimited as e:
    # A traceback here is noise: this is an expected, temporary condition with
    # an obvious remedy, and the message already says what to do.
    raise SystemExit(str(e))

print(f"Checked {result['considered']} of {result['eligible']} campgrounds in range "
      f"({result['fetched']} forecast points fetched, {result['from_cache']} cached).")

if not result["results"]:
    print("No matching days found :(")
    raise SystemExit(0)

with open(args.output, "wt", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
print(f"{result['matched']} campgrounds matched — full result written to {args.output}.")

best = result["results"][0]
day = best["days"][0]
summary = (f"{best['name']} ({best['state']}, {best['dist']} mi): "
           f"{day['day']} {day['date']} high {day['high']}F")
print(f"Best: {summary}")
if phone:
    print(wf.send_sms_notification(phone, summary))
