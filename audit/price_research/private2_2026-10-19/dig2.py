"""Second-round reading digest (2026-10-19): every '$' figure on the pages round 1 fetched, unfiltered.

Round 1's dig.py dropped a snippet when 'monthly', 'seasonal', 'cabin' etc. sat near the figure,
which hid ordinary rate tables ("Nightly $40 | Weekly $200 | Monthly $500"). This shows each
dollar figure with ~110 chars before and ~90 after, merges overlapping windows, dedupes.

    python3 -I dig2.py ST [ST ...]      the round-2 re-read ids (buckets.json) in those states
"""
import json, re, sys, os, glob
D = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(os.path.dirname(D), "private_2026-10-16")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(D)))
B = json.load(open(f"{D}/buckets.json"))
WANT = set(B["dollar_nightly"]) | set(B["dollar_no_nightly"])
cg = {e["id"]: e for e in json.load(open(f"{ROOT}/campgrounds.json"))}
states = set(sys.argv[1:])


def texts(st):
    out = {}
    for f in (f"{R1}/pages_{st}.jsonl", f"{R1}/browser_{st}.jsonl"):
        if not os.path.exists(f):
            continue
        for l in open(f):
            r = json.loads(l)
            if r["id"] not in WANT:
                continue
            for p in r.get("pages") or []:
                ls = p.get("lines")
                if not ls:
                    continue
                ls = ls if isinstance(ls, list) else [ls]
                out.setdefault(r["id"], []).append((p["url"], " | ".join(ls).replace("\n", " | ")))
    return out


norm = lambda s: re.sub(r"\s*\|\s*(\|\s*)*", " | ", re.sub(r"\s+", " ", s))
for st in sorted(states):
    for i, pages in sorted(texts(st).items()):
        e = cg.get(i)
        if not e or (e.get("fees") or {}).get("nightly_low") is not None:
            continue
        rt = e.get("rating") or {}
        print(f"## {i} {e['name']} [{e['state']}] tier={rt.get('price_tier')} stars={rt.get('stars')} "
              f"web={(e.get('website') or '').split(chr(10))[0][:70]}")
        seen, n = set(), 0
        for url, t in pages:
            t = norm(t)
            spans = []
            for m in re.finditer(r"\$\s?\d", t):
                a, b = max(0, m.start() - 110), min(len(t), m.end() + 90)
                if spans and a <= spans[-1][1]:
                    spans[-1][1] = b
                else:
                    spans.append([a, b])
            shown = False
            if re.search(r"rvlife\.com|goodsam\.com|roverpass\.com/f/|rjourney\.com/parks|gorving\.ca/(explore|rv/)|rvparky\.com", url):
                continue
            if re.search(r"\.(m4a|mp3|mp4|jpe?g|png|gif|webp|zip)(\?|$)", url, re.I):
                continue
            for a, b in spans:
                s = t[a:b]
                if sum(c.isascii() for c in s) < 0.85 * len(s):
                    continue
                k = re.sub(r"\W", "", s)[20:90]
                if k in seen:
                    continue
                seen.add(k)
                if not shown:
                    print("  @", url[:110]); shown = True
                print("   ", s[:420])
                n += 1
                if n >= 10:
                    break
            if n >= 10:
                break
