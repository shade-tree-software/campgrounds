"""Wyoming's booking links, 2026-10-12: python3 -I wy_links_2026-10-12.py [--apply]

Wyoming State Parks moved its reservations to US eDirect (reserve.wyoming.gov; the parks' fee page: 'Online* at
RESERVE.WYOMING.GOV'), and wyomingstateparks.reserveamerica.com no longer resolves. Each entry's dead link becomes its
park's page on the new site, https://reserve.wyoming.gov/web/#!park/<PlaceId> (PlaceIds from the site's citypark API,
wyordr.usedirect.com/wyomingrdr/rdr/fd/citypark); Medicine Lodge, which had no booking link, gets its own; Seminoe's
note named ReserveAmerica and now names the new site; Hawk Springs' note loses its '~$18/night' (the non-resident base
alone; the fees group has the schedule). Re-scan the two notes afterwards."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEAD = "https://wyomingstateparks.reserveamerica.com"
PLACE = {6349: 7, 6350: 8, 6351: 12, 6352: 10, 6353: 11, 6354: 6, 6359: 15, 6360: 14, 13968: 10, 13969: 10, 13976: 10,
         13977: 10}
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
n = 0
for e in rows:
    w = e.get("website") or ""
    if e["id"] in PLACE:
        lines = w.split("\n")
        assert DEAD in lines, (e["id"], w)
        e["website"] = "\n".join(f"https://reserve.wyoming.gov/web/#!park/{PLACE[e['id']]}" if l == DEAD else l for l in lines)
        n += 1
    elif e["id"] == 6361:
        assert "reserve.wyoming.gov" not in w
        e["website"] = w + "\nhttps://reserve.wyoming.gov/web/#!park/13"
        n += 1
    elif DEAD in w:
        print("not handled:", e["id"], e["name"])
    if e["id"] == 6370:
        old = "first-come, first-served, ~$18/night; max equipment length ~25 ft. --Claude"
        assert old in e["note"]
        e["note"] = e["note"].replace(old, "first-come, first-served; max equipment length ~25 ft. --Claude")
    if e["id"] == 6360:
        old = "Reservable via ReserveAmerica, FCFS off-season. --Claude"
        assert old in e["note"]
        e["note"] = e["note"].replace(old, "Reservable on reserve.wyoming.gov (US eDirect), FCFS off-season. --Claude")
print(n, "links")
if "--apply" in sys.argv:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    print("written")
