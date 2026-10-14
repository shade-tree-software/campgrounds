"""web.py [--apply]: batch 29's website and inclusion re-checks. Josephine County moved Wolf Creek Park's page
(11096: the old departments/parks/wolf_creek.php URL is a 404; the park is now _T66_R31.php). The four Linn County
parks (11014 Whitcomb Creek, 11033 River Bend, 11083 Cascadia, 11084 Edgewater) show availability on CampLife only
after a login, and Almeda (11057) is a tent campground where two sites take a self-contained RV: each gets a dated
inclusion re-check. Asserts each entry's current value first."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
T = "; re-check 2026-10-14: "
IE = {i: r.get("inclusion_evidence") for i, r in ((r["id"], r) for r in json.load(open(P, encoding="utf-8")))
      if i in (11014, 11033, 11057, 11083, 11084)}
LOGIN = "CampLife shows availability only after a login, on every date read from October 2026 to June 2027; the county also takes bookings by phone (541-967-3917)"
MOVED = {  # id: {field: (current, new)}
 11096: {"website": ("https://www.josephinecounty.gov/departments/parks/wolf_creek.php\nhttps://www.camplife.com/campground/Wolf+Creek+Park",
                     "https://www.josephinecounty.gov/parks/_T66_R31.php\nhttps://www.camplife.com/campground/Wolf+Creek+Park")},
 11014: {"inclusion_evidence": (IE[11014], IE[11014] + T + "the county's page gives no site count; it posts a $25 rate for a non-hookup site (1 RV, 2 tents) and a 2026 season of April 17 to September 20, and CampLife sells 71 back-in and 4 pull-through sites. " + LOGIN)},
 11033: {"inclusion_evidence": (IE[11033], IE[11033] + T + "the county's page gives 85 campsites, all reservable, at $37 with water and electric or $28 without (1 RV each), open year-round. " + LOGIN)},
 11057: {"inclusion_evidence": (IE[11057], IE[11057] + T + "the county's page lists 38 tent sites, two group tent sites and two yurts, and no RV sites; on CampLife only pull-through sites 02 and 03 say they take a fully self-contained RV, and the park has no hookups and no water for filling tanks")},
 11083: {"inclusion_evidence": (IE[11083], IE[11083] + T + "the county's page gives 13 first-come and 10 reservable non-hookup sites (35 ft at most, 1 RV each) at $28, open May 1 to September 27, 2026. " + LOGIN)},
 11084: {"inclusion_evidence": (IE[11084], IE[11084] + T + "the county's page gives 49 full-hookup RV sites at $45-50 a night plus 7% city lodging tax, open year-round. " + LOGIN)},
}
INSERTED = {}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, fields in MOVED.items():
    for f, (cur, new) in fields.items():
        assert cur and by[i].get(f) == cur, (i, f, by[i].get(f))
        print(i, f, repr(new)[-200:])
for i, fields in INSERTED.items():
    for f, new in fields.items():
        assert f not in by[i] and "website" in by[i], (i, f)
        print(i, f, "+", repr(new))
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    for i in sorted(set(MOVED) | set(INSERTED)):
        start = raw.index('\n    "id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        for f, (cur, new) in MOVED.get(i, {}).items():
            line = json.dumps(f) + ': ' + json.dumps(cur, ensure_ascii=False)
            assert block.count(line) == 1, (i, f)
            block = block.replace(line, json.dumps(f) + ': ' + json.dumps(new, ensure_ascii=False), 1)
        for f, new in INSERTED.get(i, {}).items():
            line = '\n    "website": ' + json.dumps(by[i]["website"], ensure_ascii=False) + ','
            assert block.count(line) == 1, (i, f)
            block = block.replace(line, line + '\n    ' + json.dumps(f) + ': ' + json.dumps(new, ensure_ascii=False) + ',', 1)
        raw = raw[:start] + block + raw[end:]
    json.loads(raw)
    open(P, "w", encoding="utf-8").write(raw)
    after = {r["id"]: r for r in json.load(open(P, encoding="utf-8"))}
    for i, fields in MOVED.items():
        for f, (cur, new) in fields.items():
            assert after[i][f] == new, (i, f)
    for i, fields in INSERTED.items():
        for f, new in fields.items():
            assert after[i][f] == new, (i, f)
    print("applied", sum(len(v) for v in MOVED.values()) + sum(len(v) for v in INSERTED.values()), "fields")
