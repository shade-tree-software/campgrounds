"""web.py [--apply]: batch 26's websites, phones and inclusion re-checks. Epsom Valley (4137) and Bay Hide Away (5083)
left CampLife for Campspot, where their own sites' booking buttons now go; Torry Island (4844) takes no online
bookings, and the city's site moved to belleglade.gov; Nashwauk (5670) gains the phone its city page gives.
Sanctuary (5117) and Rest Haven (4636) get a dated inclusion re-check. Asserts each entry's current value first;
INSERTED keys must be absent and go in after "website"."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
T = "; re-check 2026-10-14: "
IE = {i: r.get("inclusion_evidence") for i, r in ((r["id"], r) for r in json.load(open(P, encoding="utf-8")))
      if i in (4636, 4844, 5083, 5117)}
MOVED = {  # id: {field: (current, new)}
 4137: {"website": ("https://epsomvalleycampground.com/\nhttps://www.camplife.com/Epsom+Valley+Campground?newres=y",
                    "https://epsomvalleycampground.com/\nhttps://www.campspot.com/book/epsomvalleycampground")},
 4636: {"inclusion_evidence": (IE[4636], IE[4636] + T + "the park's own site posts no rate and takes bookings by phone or email; its CampLife listing (19 back-in sites) had no site open on any of 14 dates read from October 2026 to June 2027 and pitches the park to snowbirds, traveling professionals and long-term guests")},
 4844: {"website": ("https://www.bellegladegov.com/torry\nhttps://www.camplife.com/campground/Torry+Island+Campground",
                    "https://www.belleglade.gov/torry"),
        "inclusion_evidence": (IE[4844], IE[4844] + T + "the city's rates page (effective October 1, 2025) posts daily rates for full-hookup and water-and-electric RV sites; reservations are by phone, since CampLife takes none online")},
 5083: {"website": ("https://bayhideaway.com/\nhttps://www.camplife.com/campground/Bay+Hide+Away+RV+Park+&+Campground",
                    "https://bayhideaway.com/\nhttps://www.campspot.com/book/bay-hideaway-rv-park-and-campground"),
        "inclusion_evidence": (IE[5083], IE[5083] + T + "the CampLife listing is gone; the park books on Campspot, which had RV sites open on every date read from October 2026 to June 2027")},
 5117: {"inclusion_evidence": (IE[5117], IE[5117] + T + "the park's own site shows a hosting error ('Something's wrong here'), but its CampLife listing sells 24 back-in sites, open on dates read from October 2026 to June 2027")},
}
INSERTED = {5670: {"phone": "218-885-1210"}}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, fields in MOVED.items():
    for f, (cur, new) in fields.items():
        assert cur and by[i].get(f) == cur, (i, f, by[i].get(f))
        print(i, f, repr(new)[-160:])
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
