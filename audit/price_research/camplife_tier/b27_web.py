"""web.py [--apply]: batch 27's websites, phones and inclusion re-checks. West Two Rivers' city page moved to
mountainiron.gov; The Trails at Lavender Road takes no online bookings, so its CampLife line goes; Whitewater Lake's
CampLife link was a different park (Whitewater Lake, Chipley, Florida) and goes. Wagon Master gains the phone its own
pages give (the key held ""). Central State Park, Scissortail, Stephenville, Cedars and Whitewater Lake get a dated
inclusion re-check. Asserts each entry's current value first; EMPTY keys must hold "" now."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
T = "; re-check 2026-10-14: "
IE = {i: r.get("inclusion_evidence") for i, r in ((r["id"], r) for r in json.load(open(P, encoding="utf-8")))
      if i in (6829, 6834, 7826, 8295, 8314)}
EDM = "the city posts its rates publicly, but its CampLife calendar answered 'Must Login to See Availability.' on every date read from October 2026 to June 2027"
MOVED = {  # id: {field: (current, new)}
 5704: {"website": ("https://mtniron.com/parks-rec/west-two-rivers-campground/\nhttps://www.camplife.com/campground/West+Two+Rivers+Campground",
                    "https://mountainiron.gov/west-two-rivers-campground/\nhttps://www.camplife.com/campground/West+Two+Rivers+Campground")},
 6829: {"inclusion_evidence": (IE[6829], IE[6829] + T + EDM)},
 6834: {"inclusion_evidence": (IE[6834], IE[6834] + T + EDM + "; Scissortail takes bookings only on the day of arrival")},
 7826: {"inclusion_evidence": (IE[7826], IE[7826] + T + "no live web presence: randrbytheres.com does not resolve, stephenvillerv.com answers 404, and the CampLife listing 'Stephenville RV Park by the Reservoir' has no park behind it; RV Life (park 257132, formerly R&R RV Park by the Reservoir) lists no website and its newest review is from October 2023; the Good Sam directory has no record")},
 7864: {"website": ("https://www.thetrailsrvparks.com/\nhttps://www.camplife.com/campground/The+Trails+at+Lavender+Road",
                    "https://www.thetrailsrvparks.com/")},
 8295: {"inclusion_evidence": (IE[8295], IE[8295] + T + "the park's rates page prices an RV pull-through at C$89 plus HST a night for 2 people, over the ~C$55 private gate; it also sells seasonal sites (from C$2,200 a year) and lists sites for sale")},
 8314: {"website": ("https://www.greatersudbury.ca/play/campgrounds-and-trailer-parks/whitewater-lake-trailer-park/\nhttps://www.camplife.com/campground/Whitewater+Lake",
                    "https://www.greatersudbury.ca/play/campgrounds-and-trailer-parks/whitewater-lake-trailer-park/"),
        "inclusion_evidence": (IE[8314], IE[8314] + T + "the city's 2026 fee page posts overnight trailer rates and the park books by phone; the CampLife link the entry carried was a different park (Whitewater Lake, Chipley, Florida) and is removed")},
}
EMPTY = {7897: {"phone": "(940) 500-8973"}}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, fields in MOVED.items():
    for f, (cur, new) in fields.items():
        assert cur and by[i].get(f) == cur, (i, f, by[i].get(f))
        print(i, f, repr(new)[-160:])
for i, fields in EMPTY.items():
    for f, new in fields.items():
        assert by[i].get(f) == "", (i, f, by[i].get(f))
        print(i, f, "+", repr(new))
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    for i in sorted(set(MOVED) | set(EMPTY)):
        start = raw.index('\n    "id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        for f, (cur, new) in MOVED.get(i, {}).items():
            line = json.dumps(f) + ': ' + json.dumps(cur, ensure_ascii=False)
            assert block.count(line) == 1, (i, f)
            block = block.replace(line, json.dumps(f) + ': ' + json.dumps(new, ensure_ascii=False), 1)
        for f, new in EMPTY.get(i, {}).items():
            line = json.dumps(f) + ': ""'
            assert block.count(line) == 1, (i, f)
            block = block.replace(line, json.dumps(f) + ': ' + json.dumps(new, ensure_ascii=False), 1)
        raw = raw[:start] + block + raw[end:]
    json.loads(raw)
    open(P, "w", encoding="utf-8").write(raw)
    after = {r["id"]: r for r in json.load(open(P, encoding="utf-8"))}
    for i, fields in MOVED.items():
        for f, (cur, new) in fields.items():
            assert after[i][f] == new, (i, f)
    for i, fields in EMPTY.items():
        for f, new in fields.items():
            assert after[i][f] == new, (i, f)
    print("applied", sum(len(v) for v in MOVED.values()) + sum(len(v) for v in EMPTY.values()), "fields")
