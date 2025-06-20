import sys
import json
import re
import requests

# Takes a Google place URL and returns the name, lat/long, and elevation.
# Elevation is calculated by sending the lat/long to open-elevation.com.

url = sys.argv[1]

PATTERN = r'place\/(.+)\/@(-?\d{1,3}\.\d{1,9}),(-?\d{1,3}\.\d{1,9})'

match = re.search(PATTERN, url)
if match:
  name = match.group(1).replace("+", " ")
  lat = f"{float(match.group(2)):.4f}"
  lon = f"{float(match.group(3)):.4f}"
  response = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}")
  if response.status_code == 200:
    data = response.json()
    elevation = data["results"][0]["elevation"]
  else:
    elevation = None
  j = {
          "name": name,
          "location": f"{lat},{lon}",
          "elevation": elevation
      }
  print(json.dumps(j, indent=2))
  
