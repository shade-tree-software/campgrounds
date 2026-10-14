"""Render a Campspot park's own site map with chosen site types in red:
    python3 audit/private_gap_browser/campspot_map.py SLUG PARK_ID DATE GUESTS OUTPREFIX "TYPE NAME" ["TYPE NAME" ...]

Run from the repo root with the driver up (drv_server.py). It loads /book/<slug>/search/<date>/<date+1>/<guests>/map,
saves the availability JSON (OUTPREFIX_avail.json) and the map SVG (OUTPREFIX_map.svg), colours the named types'
sites red and every other site blue by each campsite's mapId, and screenshots OUTPREFIX_marked.png. It prints
type | site | rvLengthMax | mapId for every listed site. Use a date the reader already used (the `lists` keys in
campspot_tier_2026-10-13.jsonl); the slug, park id and guests string are in the same record.

Built for the 2026-10-13 waterfront re-audit (price_research/campspot_tier/waterfront_reaudit_2026-10-13.json). The
map is the operator's per-site map, which the evidence gate counts. Each type in the availability JSON also carries
the operator's photos (images.mainImage / images.slideshowImages; images.campspot.com URLs whose base64 key holds the
original filename, often a dated PXL_/IMG_ name); they decided Bear Lake 12639 and Hyclass 12925 where the satellite
predated the sites. A map is drawn, not surveyed: scale it from something measurable on the satellite (Bear Lake's
pond) before quoting metres.
"""
import sys, json, re, subprocess, datetime
slug, pid, date, guests, out = sys.argv[1:6]
want = set(sys.argv[6:])
D = ["python3", "audit/private_gap_browser/drv.py"]
def drv(*a):
    return subprocess.run(D + list(a), capture_output=True, text=True).stdout
d2 = (datetime.date.fromisoformat(date) + datetime.timedelta(days=1)).isoformat()
print(drv("goto", f"url=https://www.campspot.com/book/{slug}/search/{date}/{d2}/{guests}/map", "wait=9000").strip())
net = drv("net")
ia = [l for l in net.splitlines() if f"availability/parks/{pid}?checkin={date}" in l]
im = [l for l in net.splitlines() if "park-maps.campspot.com" in l]
ia = re.match(r"\[(\d+)\]", ia[-1]).group(1); im = re.match(r"\[(\d+)\]", im[-1]).group(1)
avail = json.loads(drv("body", f"i={ia}", "max=5000000"))
svg = drv("body", f"i={im}", "max=5000000")
json.dump(avail, open(out + "_avail.json", "w"))
open(out + "_map.svg", "w", encoding="utf-8").write(svg)
for t in avail:
    for s in t.get("campsites") or []:
        mid = s.get("mapId") or ""
        col = "#e00000" if t["name"] in want else "#0050ff"
        found = f'id="{mid}"' in svg
        if mid:
            svg = re.sub(rf'(<(?:rect|path|polygon)[^>]*?id="{re.escape(mid)}"[^>]*?)fill="[^"]*"', rf'\1fill="{col}"', svg)
            svg = re.sub(rf'(<(?:rect|path|polygon)[^>]*?)fill="[^"]*"([^>]*?id="{re.escape(mid)}")', rf'\1fill="{col}"\2', svg)
        print(("*" if t["name"] in want else " "), t["name"], "|", s.get("name"), "|", (s.get("rvInfo") or {}).get("rvLengthMax"),
              "|", mid[:28], "" if found else "MAPID-MISSING")
open(out + "_marked.svg", "w", encoding="utf-8").write(svg)
print(drv("goto", f"url=file://{out}_marked.svg", "wait=2000").strip())
print(drv("shot", f"path={out}_marked.png").strip())
