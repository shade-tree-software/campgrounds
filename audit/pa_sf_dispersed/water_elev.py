#!/usr/bin/env python3
"""Elevation (Open-Meteo DEM, the source every entry is pinned against) for each
candidate pin, and the distance from each candidate's sites to the nearest mapped
stream/river/lake (USGS NHD), which decides which clusters need a satellite look.

    python3 audit/pa_sf_dispersed/water_elev.py   # adds elevation_meters + water to candidates.json
"""
import json, math, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
NHD = "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer"
UA = {"User-Agent": "ekko-campgrounds/1.0 (personal research)"}


MIRRORS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
           "https://overpass.private.coffee/api/interpreter"]


def get(url, data=None):
    for i in range(6):
        if url in MIRRORS:
            url = MIRRORS[i % len(MIRRORS)]
        try:
            req = urllib.request.Request(url, data=data, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=180))
        except Exception as e:
            print("retry", e)
            time.sleep(3 * (i + 1))
    raise RuntimeError(url)


def seg_m(p, a, b):
    # metres from p to segment ab on a local equirectangular plane
    k = math.cos(math.radians(p[0]))
    P, A, B = [(x[1] * 111320 * k, x[0] * 110540) for x in (p, a, b)]
    dx, dy = B[0] - A[0], B[1] - A[1]
    t = 0 if dx == dy == 0 else max(0, min(1, ((P[0] - A[0]) * dx + (P[1] - A[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(P[0] - A[0] - t * dx, P[1] - A[1] - t * dy)


def main():
    path = os.path.join(HERE, "candidates.json")
    cands = json.load(open(path))
    pins = [tuple(map(float, c["location"].split(","))) for c in cands]
    for i in (range(0, len(pins), 100) if any("elevation_meters" not in c for c in cands) else []):
        chunk = pins[i:i + 100]
        r = get("https://api.open-meteo.com/v1/elevation?latitude=" + ",".join(f"{p[0]}" for p in chunk)
                + "&longitude=" + ",".join(f"{p[1]}" for p in chunk))
        for c, e in zip(cands[i:i + 100], r["elevation"]):
            c["elevation_meters"] = float(e)
    # USGS NHD (1:24k flowlines, waterbodies, wide-river areas) within 300 m of
    # any site. Overpass was tried first and 504'd on most queries.
    for c in cands:
        if "water_m" in c:
            continue
        best = (None, None)
        for ll in c["site_lls"]:
            for layer in (6, 12, 9):
                q = urllib.parse.urlencode({
                    "geometry": f"{ll[1]},{ll[0]}", "geometryType": "esriGeometryPoint", "inSR": 4326,
                    "distance": 300, "units": "esriSRUnit_Meter", "outFields": "GNIS_NAME,FTYPE",
                    "returnGeometry": "true", "outSR": 4326, "f": "json"})
                res = get(f"{NHD}/{layer}/query?{q}")
                for f in res.get("features", []):
                    g = f["geometry"]
                    for part in g.get("paths") or g.get("rings") or []:
                        pts = [(y, x) for x, y in part]
                        for a, b in zip(pts, pts[1:]):
                            d = seg_m(ll, a, b)
                            if best[0] is None or d < best[0]:
                                best = (d, f["attributes"].get("gnis_name") or
                                        {6: "unnamed stream", 12: "unnamed waterbody", 9: "river area"}[layer])
        c["water_m"] = round(best[0]) if best[0] is not None else None   # None: nothing within 300 m
        c["water"] = best[1]
        print(c["name"][:70], c["water_m"], c["water"], flush=True)
        json.dump(cands, open(path, "w"), indent=1, ensure_ascii=False)
    json.dump(cands, open(path, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
