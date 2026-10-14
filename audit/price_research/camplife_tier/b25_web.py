"""web.py [--apply]: batch 25's websites. Timberlake (1977) and Sunny Sites (2064) linked CampLife pages that sell
other parks of the same name (Timberlake Campground, Brandon MS; Sunny's Campground, Wauseon OH); each link is
replaced by the park's own Facebook page, its only web presence, and the inclusion evidence gains a dated re-check.
Asserts each entry's current value first."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
MOVED = {  # id: {field: (current, new)}
 1977: {"website": ("https://www.camplife.com/1223/reservation/step1",
                    "https://www.facebook.com/timberlake.campground.2025/"),
        "inclusion_evidence": ("VisitMO + camplife listing: 40 full-hookup RV sites + marina on Mississippi River at Elsberry, reservable -> real RV campground",
                               "VisitMO + camplife listing: 40 full-hookup RV sites + marina on Mississippi River at Elsberry, reservable -> real RV campground; re-check 2026-10-14: the CampLife link sold a different park (Timberlake Campground, Brandon MS) and is replaced; this park is live on Facebook (timberlake.campground.2025, 'Bringing back the old Timberlake Marina') and RV Life reviewers stayed in 8/2025 and 7/2026 -> still a real RV campground")},
 2064: {"website": ("https://www.camplife.com/1171/reservation/step1",
                    "https://www.facebook.com/p/Sunny-Sites-Campground-100095036477587/"),
        "inclusion_evidence": ("rvparksnear.me/RV Life + camplife reservation: 15 large cement full-hookup sites (30/50A, W/S) off I-35 Bethany, reservable online -> real RV campground",
                               "rvparksnear.me/RV Life + camplife reservation: 15 large cement full-hookup sites (30/50A, W/S) off I-35 Bethany, reservable online -> real RV campground; re-check 2026-10-14: the CampLife link sold a different park (Sunny's Campground, Wauseon OH) and is replaced; this park is live on Facebook (Sunny Sites Campground, 495 S 39th St, Bethany) and RV Life reviewers stayed in 7/2026, 9/2026 and 10/2026 -> still a real RV campground")},
}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, fields in MOVED.items():
    for f, (cur, new) in fields.items():
        assert by[i].get(f) == cur, (i, f, by[i].get(f))
        print(i, f, repr(new)[:140])
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    for i, fields in MOVED.items():
        start = raw.index('"id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        for f, (cur, new) in fields.items():
            line = json.dumps(f) + ': ' + json.dumps(cur, ensure_ascii=False)
            assert block.count(line) == 1, (i, f)
            block = block.replace(line, json.dumps(f) + ': ' + json.dumps(new, ensure_ascii=False), 1)
        raw = raw[:start] + block + raw[end:]
    json.loads(raw)
    open(P, "w", encoding="utf-8").write(raw)
    after = {r["id"]: r for r in json.load(open(P, encoding="utf-8"))}
    for i, fields in MOVED.items():
        for f, (cur, new) in fields.items():
            assert after[i][f] == new, (i, f)
    print("applied", sum(len(v) for v in MOVED.values()), "fields")
