import requests
import sys
import json

input_filename = sys.argv[1]
output_filename = sys.argv[2]

url = "https://api.open-elevation.com/api/v1/lookup"

with open(input_filename, "rt") as f:
    input_data = json.loads(f.read())

        #{"latitude": 40.714, "longitude": -74.006},  # New York City
        #{"latitude": 48.858, "longitude": 2.295}     # Paris

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
