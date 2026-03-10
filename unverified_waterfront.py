import sys
import json

with open("all-campgrounds.json", "rt") as f:
  j = json.loads(f.read())
for c in j:
  if c["state"] == sys.argv[1] and "note" not in c:
    print(f"{c["name"]} missing note")
  elif c["state"] == sys.argv[1] and not c["waterfront"] == "none" and not (c["note"].endswith("--AWH") or c["note"].endswith("--Claude")):
    print(c["name"])
