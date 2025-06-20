import requests
import re
import pandas as pd
import sys
import time
import random
import json

# This code attempts to clean up a Google Take-Out places CSV file
# by converting it to JSON and querying the Google-provided URL to
# obtain the lat/long of each place.  In order to not trip Google's
# limit on how many of these requests can be done at once, there
# is a random delay of roughly one minute in between each request.
# Thus a long Take-Out file may take several hours to process.
#
# The code also attempts to extract an elevation from the string
# value in the Note column.  However, this is somewhat redundant
# if further processing is going to be done to obtain elevations
# from open-elevation.com.
#
# The name value is created by first looking to see if the labels
# file has an entry with the same lat/long.  If not, the value
# from the Title column is used.

LAT_LONG_1 = r'(-?\d{1,3}\.\d{1,9}),(-?\d{1,3}\.\d{1,9})'
LAT_LONG_2 = r'@(-?\d{1,3}\.\d{1,9}),(-?\d{1,3}\.\d{1,9})'
ELEVATION = r'(\d{3,5}) ?ft\.? elev\.?\n?'

filename = sys.argv[1]
df = pd.read_csv(filename)

if len(sys.argv) > 2:
    start = int(sys.argv[2])
else:
    start = 0

if len(sys.argv) > 3:
    stop = int(sys.argv[3])
else:
    stop = len(df)

with open("labels.json", "rt") as f:
    labels = json.loads(f.read())

def get_lat_long(url):
    loc = None
    label = None
    if isinstance(url, str):
        match = re.search(LAT_LONG_1, url)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            loc = f"{lat:.4f},{lon:.4f}"
            label = labels.get(loc, None)
        else:
            if stop - start != 1:
                time.sleep(random.randint(30,90))
            response = requests.get(url)
            if response.status_code == 200:
                data = response.text
                match = re.search(LAT_LONG_2, data)
                if match:
                    lat = float(match.group(1))
                    lon = float(match.group(2))
                    loc = f"{lat:.4f},{lon:.4f}"
    return loc, label

for i in range(start, stop):
    loc, label = get_lat_long(df.iloc[i]["URL"])
    if loc is not None:
      if label is None:
          label = df.iloc[i]['Title']
      elem = {"index":i,"location":loc,"name":label}
      if not pd.isnull(df.iloc[i]['Note']):
          note = df.iloc[i]['Note']
          match = re.search(ELEVATION, note)
          if match:
              elem["elevation"] = int(match.group(1))
              note = re.sub(ELEVATION, "", note)
          elem["note"] = note
      print(f"{json.dumps(elem, indent=2)},")
