"""web.py [--apply]: batch 21's websites and phones. Marsh Park (3488) gains its vendor's campground page, where the
rates are, between the county's page and the RoverPass listing; Osage Prairie (1982) gains the phone its own pages
and RoverPass listing give (it had none). Asserts each entry's current value first."""
import json, sys
P = "/home/andrew/Dev/campgrounds/campgrounds.json"
SHEB = "https://www.sheboygancounty.com/departments/departments-f-q/planning-and-conservation/facilities/parks/sheboygan-marsh-park-campground"
MOVED = {  # id: (current website, new website)
 3488: (SHEB + "\nhttps://www.roverpass.com/c/sheboygan-broughton-marsh-park-campground-elkhart-lake-wi/",
        SHEB + "\nhttps://www.threeguysandagrill.com/pages/our-marsh-campground\nhttps://www.roverpass.com/c/sheboygan-broughton-marsh-park-campground-elkhart-lake-wi/"),
}
NEWPH = {  # id: phone, for an entry with no phone key: inserted after its website line
 1982: "417-667-2267",
}
data = json.load(open(P, encoding="utf-8"))
by = {r["id"]: r for r in data}
for i, (cur, new) in MOVED.items():
    assert by[i].get("website") == cur, (i, by[i].get("website"))
    print(i, repr(new))
for i, ph in NEWPH.items():
    assert "phone" not in by[i], (i, by[i].get("phone"))
    print(i, "phone", ph)
if "--apply" in sys.argv:
    raw = open(P, encoding="utf-8").read()
    for i, (cur, new) in MOVED.items():
        start = raw.index('"id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        line = '"website": ' + json.dumps(cur, ensure_ascii=False)
        assert block.count(line) == 1, i
        raw = raw[:start] + block.replace(line, '"website": ' + json.dumps(new, ensure_ascii=False), 1) + raw[end:]
    for i, ph in NEWPH.items():
        start = raw.index('"id": %d,' % i)
        end = raw.index('\n  }', start)
        block = raw[start:end]
        line = '"website": ' + json.dumps(by[i]["website"], ensure_ascii=False) + ",\n"
        assert block.count(line) == 1, i
        k = block.index(line) + len(line)
        indent = block[block.rfind("\n", 0, block.index(line)) + 1:block.index(line)]
        raw = raw[:start] + block[:k] + indent + '"phone": ' + json.dumps(ph) + ",\n" + block[k:] + raw[end:]
    json.loads(raw)
    open(P, "w", encoding="utf-8").write(raw)
    after = {r["id"]: r for r in json.load(open(P, encoding="utf-8"))}
    for i, (cur, new) in MOVED.items():
        assert after[i]["website"] == new, i
    for i, ph in NEWPH.items():
        assert after[i]["phone"] == ph, i
    print("applied", len(MOVED), "websites and", len(NEWPH), "phones")
