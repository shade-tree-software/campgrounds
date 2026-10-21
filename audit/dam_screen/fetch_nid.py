#!/usr/bin/env python3
"""Cache the US National Inventory of Dams (location, height, length, size) for the dam screen.

    python3 -I audit/dam_screen/fetch_nid.py

Reads the NID_v1 feature layer USACE publishes on ArcGIS Online (the nid.sec.usace.army.mil
download refuses plain HTTP) in pages of 2,000, a few fields only, and writes
audit/dam_screen/nid_cache.json (gitignored; ~93k dams). Rerun to refresh.
"""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nid_cache.json")
LAYER = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/NID_v1/FeatureServer/0/query"
FIELDS = "OBJECTID,NIDID,NAME,STATE,LATITUDE,LONGITUDE,NID_HEIGHT,DAM_LENGTH,SURFACE_AREA,NORMAL_STORAGE,RIVER_OR_STREAM,PRIMARY_DAM_TYPE,DATA_UPDATED"


def page(after):
    q = urllib.parse.urlencode({"where": f"OBJECTID>{after}", "outFields": FIELDS, "orderByFields": "OBJECTID",
                                "returnGeometry": "false", "resultRecordCount": 2000, "f": "json"})
    req = urllib.request.Request(f"{LAYER}?{q}", headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=120))["features"]


if __name__ == "__main__":
    dams, after = [], 0
    while True:
        feats = page(after)
        if not feats:
            break
        dams += [f["attributes"] for f in feats]
        after = feats[-1]["attributes"]["OBJECTID"]
        print(len(dams), flush=True)
        time.sleep(0.5)
    dams = [d for d in dams if d.get("LATITUDE") and d.get("LONGITUDE")]
    with open(OUT, "w") as f:
        json.dump(dams, f)
    print("wrote", len(dams), "dams with coordinates")
