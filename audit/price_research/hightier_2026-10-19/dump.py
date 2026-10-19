"""dump.py FROM_LINE TO_LINE -> readable rate snippets per target (pages.jsonl + wb.jsonl)."""
import json, sys, re
cg = {e["id"]: e for e in json.load(open("/home/andrew/Dev/campgrounds/campgrounds.json"))}
P = [json.loads(l) for l in open("pages.jsonl")]
W = {}
for l in open("wb.jsonl"):
    r = json.loads(l); W[r["id"]] = r
a, b = int(sys.argv[1]), int(sys.argv[2])
for r in P[a:b]:
    e = cg.get(r["id"])
    if not e: continue
    print(f"\n##### {r['id']} {e['state']} {e['name']} | {e.get('website','')[:80]} | gs={bool((e.get('discounts') or {}).get('good_sam'))} | fees={(e.get('fees') or {}).get('nightly_low')}")
    print("NOTE:", (e.get("note") or "")[:300])
    seen = set()
    for p in r["pages"]:
        sn = [s for s in p["snip"] if s[150:230] not in seen]
        for s in sn: seen.add(s[150:230])
        if sn:
            print(f"  -- {p['url'][:110]}")
            for s in sn[:8]: print("     ", s.replace("\n", " ")[:330])
    if r["err"]: print("  ERR", r["err"][:2])
    w = W.get(r["id"])
    if w:
        for c in w["caps"]:
            sn = [s for s in c["snip"] if s[150:230] not in seen]
            if sn:
                print(f"  WB {c['ts'][:8]} {c['url'][:100]}")
                for s in sn[:5]: print("     ", s[:300])
