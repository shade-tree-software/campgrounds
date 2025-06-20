import requests
import sys
import json

# This code uses the open-elevation API to add/update all elevation values
# for each campsite in the input JSON list data.  The format of the input
# data is:
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
#    "note": "https://thedyrt.com/press/2025-best-places-to-camp-in-the-southeast-region/"
#  },
#  ...
# ]
#
# Note that elevation is optional.  If it exists it will be updated.
# If it does not exist it will be added.  Units are in meters.
#
# Note that the format of the location string is important because it is
# used as a key.  It must be a latitude with exactly four decimal places
# of precision followed by a comma, no space, and a longitude with exactly
# four decimal places of precision.
#
# This code uses the POST version of the open-elevation API to retrieve
# all elevation values in one API call.  To obtain just one elevation
# value on the command line, you can use the GET version as follows:
#
# curl 'https://api.open-elevation.com/api/v1/lookup?locations=38.2474,-78.6704'
#

input_filename = sys.argv[1]
output_filename = sys.argv[2]

url = "https://api.open-elevation.com/api/v1/lookup"

with open(input_filename, "rt") as f:
    input_data = json.loads(f.read())

payload = {
    "locations": [
    ]
}
input_hash = {}
for elem in input_data:
    input_hash[elem["location"]] = elem
    latitude,longitude = elem["location"].split(",")
    payload["locations"].append({
        "latitude": float(latitude),
        "longitude": float(longitude)
    })

# Send the POST request
try:
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract and print elevation data
        for result in data["results"]:
            lat = f"{result['latitude']:.4f}"
            lon = f"{result['longitude']:.4f}"
            loc = f"{lat},{lon}"
            input_hash[loc]["elevation"] = result["elevation"]
    else:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

output_data = list(input_hash.values())
with open(output_filename, "wt") as f:
    f.write(json.dumps(output_data, indent=2))
