"""Print a reading digest of local_pages.py output: per entry, deduplicated dollar lines per page.
python3 -I local_digest.py PAGES.jsonl [--from ID]"""
import json, sys
start = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
for l in open(sys.argv[1]):
    r = json.loads(l)
    if r["id"] < start:
        continue
    print(f"## {r['id']} {r['name']}")
    seen = set()
    for p in r["pages"]:
        if p.get("error") or p.get("pdf"):
            print(f"   [{p['url'][:90]}] {'PDF' if p.get('pdf') else p['error'][:60]}")
            continue
        new = [x for x in p.get("lines", []) if x[150:300] not in seen]
        for x in new:
            seen.add(x[150:300])
        if new:
            print(f"   [{p['url'][:90]}]")
            for x in new[:6]:
                print("      ", x[60:400])
