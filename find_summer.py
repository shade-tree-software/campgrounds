import requests
import json
from datetime import datetime
from geopy.distance import great_circle

HOME = (38.9295911, -77.3668801)

def get_day_of_week(date_str):
  date_obj = datetime.strptime(date_str, '%Y-%m-%d')
  day_name = date_obj.strftime('%A')
  return day_name

with open("all-campgrounds.json", "rt") as f:
  j = f.read()
  campgrounds = json.loads(j)

summers = []
for campground in campgrounds:
  name = campground["name"]
  print(f"Checking {name}")
  lat, long = campground["location"].split(",")
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
    if temp and temp >= 70 and temp <= 88:
      date = data["daily"]["time"][index]
      day = get_day_of_week(date)
      point = (float(lat), float(long))
      dist = great_circle(HOME, point).miles
      if day in ["Saturday","Sunday"]:
        summer = {
          "dist": dist,
          "date": date,
          "day": day,
          "temp": temp,
          "name": name
        }
        print(json.dumps(summer))
        summers.append(summer)
sorted_summers = sorted(summers, key=lambda d: d['dist'])
with open("sorted_summer_days.json", "wt") as f:
  f.write(json.dumps(sorted_summers, indent=2))
