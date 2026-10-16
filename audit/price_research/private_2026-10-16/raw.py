"""raw.py ST id [grep]  - all captured lines of one entry (optionally only those matching grep)"""
import json, re, sys
st, i = sys.argv[1], int(sys.argv[2]); g = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 else None
for l in open(f"{__import__('os').path.dirname(__file__)}/pages_{st}.jsonl"):
    r = json.loads(l)
    if r["id"] != i: continue
    for p in r["pages"]:
        print("[", p["url"], "]")
        for x in p.get("lines", []):
            if not g or g.search(x): print("   ", re.sub(r"(\s*\|\s*)+", " | ", x)[:420])
