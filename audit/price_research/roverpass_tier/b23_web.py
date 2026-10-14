"""web.py [--apply]: batch 23's phones. Bridgeview (7414) and Kountry Ranch (7600) had an empty phone and gain the one
their own pages give; Cozy Acres (7475) swaps a number found on none of its pages for the one its booking page gives
('Call (430)-247-7019 to Book Your Stay'). Asserts each entry's current value first."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
FILLPH = {  # id: phone, for an entry whose phone is the empty string
 7414: "254-559-8582",
 7600: "979-230-6101",
}
SWAPPH = {  # id: (current phone, new phone)
 7475: ("903-646-5839", "430-247-7019"),
}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, ph in FILLPH.items():
    assert by[i].get("phone") == "", (i, by[i].get("phone"))
    print(i, "phone", ph)
for i, (cur, new) in SWAPPH.items():
    assert by[i].get("phone") == cur, (i, by[i].get("phone"))
    print(i, "phone", cur, "->", new)
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    def edit(raw, i, old, new):
        start = raw.index('"id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        assert block.count(old) == 1, i
        return raw[:start] + block.replace(old, new, 1) + raw[end:]
    for i, ph in FILLPH.items():
        raw = edit(raw, i, '"phone": ""', '"phone": ' + json.dumps(ph))
    for i, (cur, new) in SWAPPH.items():
        raw = edit(raw, i, '"phone": ' + json.dumps(cur), '"phone": ' + json.dumps(new))
    json.loads(raw)
    open(P, "w", encoding="utf-8").write(raw)
    after = {r["id"]: r for r in json.load(open(P, encoding="utf-8"))}
    for i, ph in FILLPH.items():
        assert after[i]["phone"] == ph, i
    for i, (cur, new) in SWAPPH.items():
        assert after[i]["phone"] == new, i
    print("applied", len(FILLPH) + len(SWAPPH), "phones")
