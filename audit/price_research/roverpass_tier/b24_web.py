"""web.py [--apply]: batch 24's websites. The Preserve (7861) swaps its dead /rv-resorts/ page (HTTP 404) for the
development's home page; Tin Valley (7870) drops tinvalleyretrorentals.com, which answers 'Website unavailable'
(HTTP 402), keeping the RoverPass listing it books through. Asserts each entry's current value first."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
PRES = "https://www.roverpass.com/c/the-preserve-of-texas-cleveland-tx/"
TINV = "https://www.roverpass.com/c/tin-valley-rv-park-terlingua-tx/"
MOVED = {  # id: (current website, new website)
 7861: ("https://www.preserveoftexas.com/rv-resorts/\n" + PRES, "https://www.preserveoftexas.com/\n" + PRES),
 7870: ("https://tinvalleyretrorentals.com\n" + TINV, TINV),
}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, (cur, new) in MOVED.items():
    assert by[i].get("website") == cur, (i, by[i].get("website"))
    print(i, repr(new))
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    for i, (cur, new) in MOVED.items():
        start = raw.index('"id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        line = '"website": ' + json.dumps(cur, ensure_ascii=False)
        assert block.count(line) == 1, i
        raw = raw[:start] + block.replace(line, '"website": ' + json.dumps(new, ensure_ascii=False), 1) + raw[end:]
    json.loads(raw)
    open(P, "w", encoding="utf-8").write(raw)
    after = {r["id"]: r for r in json.load(open(P, encoding="utf-8"))}
    for i, (cur, new) in MOVED.items():
        assert after[i]["website"] == new, i
    print("applied", len(MOVED), "websites")
