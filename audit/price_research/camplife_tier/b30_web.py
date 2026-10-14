"""web.py [--apply]: batch 30's websites, phone and inclusion re-checks. Crazy Horse (10147) left CampLife for
ResNexus, where its own site's booking links now go; Newport Founders (10507) had CampLife id 331, which is a
different park (Newport RV Park, Portsmouth RI), and the city's 'Book A Spot!' link goes to ResNexus; Copperfield
(11131) gains its CampLife listing and the reservation phone that listing gives. Asserts each entry's current value
first (Copperfield's phone is the one empty current value allowed)."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
T = "; re-check 2026-10-14: "
IE = {i: r.get("inclusion_evidence") for i, r in ((r["id"], r) for r in json.load(open(P, encoding="utf-8")))
      if i in (10147, 10507)}
CP = "https://www.idahopower.com/community-recreation/recreation/parks-and-campgrounds/copperfield-park/"
MOVED = {  # id: {field: (current, new)}
 10147: {"website": ("https://www.crazyhorservresort.com/\nhttps://www.camplife.com/campground/Crazy+Horse+RV+Resort",
                     "https://www.crazyhorservresort.com/\nhttps://resnexus.com/resnexus/reservations/book/4973D9DF-C2F0-499A-A69D-DB906EF61A1F/?NewSearch=1"),
         "inclusion_evidence": (IE[10147], IE[10147] + T + "the CampLife listing is gone; the park books on ResNexus, whose standard rate was $55 a night on both back-in and pull-through RV sites for 2026-10-14, and its own rates page posts daily rates")},
 10507: {"website": ("https://newport-wa.org/newport-founders-rv-park/\nhttps://www.camplife.com/331/reservation/",
                     "https://newport-wa.org/newport-founders-rv-park/\nhttps://resnexus.com/resnexus/reservations/book/A73CD340-A8E8-40AC-B093-6D55D9EFE391/map?tabID=4&mapID=2"),
         "inclusion_evidence": (IE[10507], IE[10507] + T + "the old CampLife link (id 331) was a different park, Newport RV Park in Portsmouth RI; the city's page posts $50 a night and books through ResNexus, open April 15 to October 15")},
 11131: {"website": (CP, CP + "\nhttps://www.camplife.com/campground/Hells+Canyon+Area+-+Copperfield+Park"),
         "phone": ("", "1-844-472-7275")},
}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, fields in MOVED.items():
    for f, (cur, new) in fields.items():
        assert (cur or (i, f) == (11131, "phone")) and by[i].get(f) == cur, (i, f, by[i].get(f))
        print(i, f, repr(new)[-150:])
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    for i in sorted(MOVED):
        start = raw.index('\n    "id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        for f, (cur, new) in MOVED[i].items():
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
