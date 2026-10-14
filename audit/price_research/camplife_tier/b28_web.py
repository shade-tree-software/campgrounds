"""web.py [--apply]: batch 28's websites, phones and inclusion re-checks. Lobies gains the town's campground page in
place of a tourism listing; George Lane books by phone (its CampLife listing sells no site), so the CampLife line goes;
Scout and North Park's links pointed at CampLife's generic idaho_power page and now name their own listings. Golden
Lake, Entwistle, McCormick and Bonner County gain the phones their own pages give (the keys held ""). Roth Park, Golden
Lake, George Lane and Hells Canyon get a dated inclusion re-check. Asserts each entry's current value first; EMPTY keys
must hold "" now."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
T = "; re-check 2026-10-14: "
IE = {i: r.get("inclusion_evidence") for i, r in ((r["id"], r) for r in json.load(open(P, encoding="utf-8")))
      if i in (8331, 8342, 9074, 9615)}
IP = "https://www.idahopower.com/community-recreation/recreation/parks-and-campgrounds/"
MOVED = {  # id: {field: (current, new)}
 8331: {"inclusion_evidence": (IE[8331], IE[8331] + T + "the park's 2026 rate sheet prices an overnight 30-amp site at C$55 off-season and C$60 in July and August and a premium 50-amp site at C$60-65 (long weekends C$70-75), before HST and the 4% municipal accommodation tax, so peak rates are over the ~C$55 private gate; CampLife sells 16 RV and tent sites online, no page states how many sites are seasonal, and seasonal sites have a waiting list")},
 8334: {"website": ("https://www.camplife.com/campground/Lobies+Campground\nhttps://visitwalkerton.com/profile/lobies-park-campground-/4319/",
                    "https://www.brockton.ca/parks-recreation-culture/lobies-park-campground/\nhttps://www.camplife.com/campground/Lobies+Campground")},
 8342: {"inclusion_evidence": (IE[8342], IE[8342] + T + "the park's 2026 rates run C$43 (unserviced) to C$64 (waterfront) and CampLife's June 2027 estimates C$45-67, before HST and a C$10 reservation fee, so the serviced sites are over the ~C$55 private gate; it also rents seasonal sites (C$2,100-3,300 plus tax and electricity) and lists RVs for sale")},
 9074: {"website": ("https://georgelanecampground.ca/\nhttps://www.camplife.com/campground/George+Lane+Campground",
                    "https://georgelanecampground.ca/"),
        "inclusion_evidence": (IE[9074], IE[9074] + T + "the campground books by phone at C$40 a night, GST included; its CampLife listing sells no site ('Park is open May 1 - Sept 30. Please select different dates.' on every date read from October 2026 to June 2027)")},
 9615: {"inclusion_evidence": (IE[9615], IE[9615] + T + "Idaho Power posts its rates publicly, but the park's CampLife calendar answered 'You must be logged in to see availablility' on every date read from October 2026 to June 2027")},
 9722: {"website": (IP + "scout-park/\nhttps://www.camplife.com/idaho_power",
                    IP + "scout-park/\nhttps://www.camplife.com/campground/CJ+Strike+Area+-+Scout+Park")},
 9723: {"website": (IP + "north-park/\nhttps://www.camplife.com/idaho_power",
                    IP + "north-park/\nhttps://www.camplife.com/campground/CJ+Strike+Area+-+North+Park")},
}
EMPTY = {8342: {"phone": "(613) 757-0018"}, 9139: {"phone": "780-719-9009"}, 9602: {"phone": "1-844-472-7275"},
         9805: {"phone": "208-263-8414"}}
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
