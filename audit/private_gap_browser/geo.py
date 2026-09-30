import sys, json, urllib.request, urllib.parse
a = sys.argv[1]
u = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?" + urllib.parse.urlencode({"address": a, "benchmark": "Public_AR_Current", "format": "json"})
r = json.load(urllib.request.urlopen(u, timeout=30))
for m in r["result"]["addressMatches"]: print(m["matchedAddress"], round(m["coordinates"]["y"],5), round(m["coordinates"]["x"],5))
