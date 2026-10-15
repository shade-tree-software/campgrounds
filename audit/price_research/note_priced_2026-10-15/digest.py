"""Compact digest for the note-priced private pass: the note's price phrase, then each page's $ snippets that
mention a night/day/site/RV word (trimmed to 150 chars around the $). python3 -I digest.py pages.jsonl [FROM [TO]]"""
import json, re, sys
ROOT = "/home/andrew/Dev/campgrounds/"
db = {r["id"]: r for r in json.load(open(ROOT + "campgrounds.json", encoding="utf-8"))}
P = re.compile(r".{0,60}\$\s?\d{2,3}.{0,60}", re.I)
W = re.compile(r"night|nightly|daily|/day|per day|a day|/nt|site|rv|hook|electric|full|w/e|camp", re.I)
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
for l in open(sys.argv[1]):
    r = json.loads(l)
    if not lo <= r["id"] <= hi:
        continue
    e = db[r["id"]]
    m = [x.group(0) for x in re.finditer(r"[^.]{0,80}\$\s?\d[^.]{0,80}", e.get("note") or "")]
    print(f"## {r['id']} {e['name']} [{e['state']}] tier={((e.get('rating') or {}).get('price_tier'))}")
    print("   NOTE:", " || ".join(m)[:400])
    for p in r["pages"]:
        if "error" in p:
            print("   ERR", p["url"][:90], p["error"][:60]); continue
        seen = []
        for x in p.get("lines", []):
            for s in re.finditer(r".{0,90}\$\s?\d[\d.,]*.{0,70}", x):
                t = s.group(0)
                if W.search(t) and t[60:120] not in "".join(seen):
                    seen.append(t)
        if seen:
            print("   [" + p["url"][:100] + "]")
            for t in seen[:8]:
                print("      ", t.replace("\n", " "))
