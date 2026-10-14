"""web.py [--apply]: batch 22's websites and phones. Jacksonville Equestrian Center (4833) swaps a dead link (its old
/services/rv-reservations/ page now lands on a local-services list) for the center's RV reservations page; Beeville
(7391) gains its own domain, which forwards to a CampLife booking page. Tumbleweed (6779), Apache Park and Trail (7365)
and Blue Dog (7401) had an empty phone and gain the one their RoverPass record or own pages give. Asserts each entry's
current value first."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
MOVED = {  # id: (current website, new website)
 4833: ("https://jaxequestriancenter.com/services/rv-reservations/\nhttps://www.roverpass.com/c/jacksonville-equestrian-center-jacksonville-fl/",
        "https://jaxequestriancenter.com/rv-reservations/\nhttps://www.roverpass.com/c/jacksonville-equestrian-center-jacksonville-fl/"),
 7391: ("https://www.roverpass.com/c/beeville-rv-park-beeville-tx/",
        "https://www.beevillervpark.com/\nhttps://www.roverpass.com/c/beeville-rv-park-beeville-tx/"),
}
FILLPH = {  # id: phone, for an entry whose phone is the empty string
 6779: "580-273-2054",
 7365: "469-325-6075",
 7401: "806-336-2024",
}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, (cur, new) in MOVED.items():
    assert by[i].get("website") == cur, (i, by[i].get("website"))
    print(i, repr(new))
for i, ph in FILLPH.items():
    assert by[i].get("phone") == "", (i, by[i].get("phone"))
    print(i, "phone", ph)
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    def edit(raw, i, old, new):
        start = raw.index('"id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        assert block.count(old) == 1, i
        return raw[:start] + block.replace(old, new, 1) + raw[end:]
    for i, (cur, new) in MOVED.items():
        raw = edit(raw, i, '"website": ' + json.dumps(cur, ensure_ascii=False), '"website": ' + json.dumps(new, ensure_ascii=False))
    for i, ph in FILLPH.items():
        raw = edit(raw, i, '"phone": ""', '"phone": ' + json.dumps(ph))
    json.loads(raw)
    open(P, "w", encoding="utf-8").write(raw)
    after = {r["id"]: r for r in json.load(open(P, encoding="utf-8"))}
    for i, (cur, new) in MOVED.items():
        assert after[i]["website"] == new, i
    for i, ph in FILLPH.items():
        assert after[i]["phone"] == ph, i
    print("applied", len(MOVED), "websites and", len(FILLPH), "phones")
