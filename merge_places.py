import sys
import json

filename = sys.argv[1]

with open(filename, "rt") as f:
    text = f.read()

input_data = json.loads(text)
output_data = {}
for feature in input_data["features"]:
    lat = feature["geometry"]["coordinates"][1]
    lon = feature["geometry"]["coordinates"][0]
    label = feature["properties"].get("name","")
    loc = f"{lat:.4f},{lon:.4f}"
    output_data[loc] = label
print(json.dumps(output_data, indent=2))
