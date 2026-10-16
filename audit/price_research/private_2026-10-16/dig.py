"""Compact reading digest for this pass: per entry, the dollar snippets near camping words, deduped, short.
python3 -I dig.py PAGES.jsonl"""
import json, re, sys
KEEP = re.compile(r"night|daily|day\b|per site|rv|site|hook|amp|full|w/e|water|electric|nightly|rate|camp|trailer|back.?in|pull", re.I)
BAD = re.compile(r"USD / Night|Claim my Campground|cabin|cottage|propane|storage|firewood|ice\b|golf cart|seasonal|monthly|month|winteriz|deposit|refund|pump.?out|lodge|motel|room", re.I)
for l in open(sys.argv[1]):
    r = json.loads(l)
    out, seen = [], set()
    for p in r["pages"]:
        for x in p.get("lines", []):
            m = x[200:240]
            for mm in re.finditer(r"\$\s?\d[\d,.]*", x[180:260]):
                pass
            s = x[60:400]
            key = s[100:160]
            if key in seen: continue
            seen.add(key)
            core = x[150:280]
            if not KEEP.search(core) or BAD.search(x[190:260]): continue
            out.append(re.sub(r"\s*\|\s*(\|\s*)*", " | ", s))
    errs = [p["error"][:30] for p in r["pages"] if p.get("error")]
    print(f"## {r['id']} {r['name'][:40]}" + (f"  ERR {errs[0]}" if errs and not out else "") + ("" if out or errs else "  (no $)"))
    for s in out[:5]:
        print("   ", s)
