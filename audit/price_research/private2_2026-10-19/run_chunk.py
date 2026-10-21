"""Second private-pricing round (2026-10-19): apply one hand-read chunk.

    python3 -I run_chunk.py NAME [--apply]        reads rows_NAME.txt; dry run without --apply

rows_NAME.txt lines (fields split on ' | '):
    ID | LOW | HIGH | fees note | quote        a rate read on the park's own page (quote must appear on a
                                              page round 1 fetched; CAD for provinces; base rate, before tax)
    min ID | SPEC | quote                     a 2-night (or weekend/holiday) minimum: SPEC as in minstay.py
    keep ID | reason                          over the limit as posted but not before tax (say so)
    drop ID | reason                          a criteria failure (minimum over 2 nights, membership, ...)
    skip ID | reason                          read, not priced: why (kept in left_NAME.json for round 3)
    # comment

After the prices are set, a private park whose base rate is over US$50 / C$69 is dropped unless an
exception applies (named, --AWH note, Good Sam rate, gateways.py, a trip stayed there) - AWH 2026-10-19.
Every drop is logged to ../dropped_2026-10-19.jsonl.
"""
import json, os, re, sys, datetime
D = os.path.dirname(os.path.abspath(__file__))
PR = os.path.dirname(D)
ROOT = os.path.dirname(os.path.dirname(PR))
R1 = f"{PR}/private_2026-10-16"
sys.path[:0] = [ROOT, PR]
from edit_entries import edit           # noqa: E402
import campground_schema as cs          # noqa: E402
import gateways, trips                  # noqa: E402

name = sys.argv[1]; APPLY = "--apply" in sys.argv
CAD = {"AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK"}
LIMIT = {"USD": 50, "CAD": 69}
NAMED = {3363, 14435}  # the Fort Myers ids left 2026-10-21: family homes are gateways now (gateways.py)
TODAY = datetime.date.today().isoformat()
cg = {e["id"]: e for e in json.load(open(f"{ROOT}/campgrounds.json"))}
norm = lambda s: re.sub(r"\s*\|\s*(\|\s*)*", " | ", re.sub(r"\s+", " ", s)).strip()

pages = {}
for st in {cg[i]["state"] for i in cg if cg[i].get("kind") == "campground"}:
    for f in (f"{R1}/pages_{st}.jsonl", f"{R1}/browser_{st}.jsonl"):
        if os.path.exists(f):
            for l in open(f):
                r = json.loads(l)
                for p in r.get("pages") or []:
                    ls = p.get("lines")
                    if ls:
                        ls = ls if isinstance(ls, list) else [ls]
                        pages.setdefault(r["id"], []).append((p["url"], norm(" | ".join(ls).replace("\n", " | "))))


def where(i, q):
    q = norm(q)
    for u, t in pages.get(i, []):
        if q in t:
            return u
    return None


num = lambda v: float(v) if "." in v else int(v)
prices, mins, drops, skips, keeps, bad = {}, {}, {}, {}, {}, []
for ln in open(f"{D}/rows_{name}.txt"):
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    kind = ln.split()[0]
    if kind in ("drop", "skip", "min", "keep"):
        parts = [x.strip() for x in ln[len(kind):].split("|")]
        i = int(parts[0])
        if kind == "drop":
            drops[i] = parts[1]
        elif kind == "keep":
            keeps[i] = parts[1]
        elif kind == "skip":
            skips[i] = parts[1]
        else:
            u = where(i, parts[2])
            if not u:
                bad.append(i); continue
            mins[i] = (parts[1], u, parts[2])
        continue
    i, lo, hi, note, q = [x.strip() for x in ln.split("|", 4)]
    i = int(i); u = where(i, q)
    if not u:
        bad.append(i); continue
    e = cg[i]
    if (e.get("fees") or {}).get("nightly_low") is not None:
        print("ALREADY PRICED", i); continue
    cur = "CAD" if e["state"] in CAD else "USD"
    prices[i] = ({"nightly_low": num(lo), "nightly_high": num(hi), "currency": cur, "checked": "2026", "note": note},
                 f"{u} ('{q}', read 2026-10-16)")
if bad:
    sys.exit(f"QUOTE NOT FOUND for {bad}")

# the price gate on what this chunk priced
gate_kept = {}
for i, (f, src) in prices.items():
    e = cg[i]
    if e["ownership"] not in ("private", "hipcamp") or f["nightly_low"] <= LIMIT[f["currency"]]:
        continue
    lat, lng = map(float, e["location"].split(","))
    why = keeps.get(i)
    if why:
        pass
    elif i in NAMED:
        why = "named exception"
    elif "AWH" in (e.get("note") or ""):
        why = "AWH's own note"
    elif (e.get("discounts") or {}).get("good_sam") and f["nightly_low"] * 0.9 <= LIMIT[f["currency"]]:
        why = "Good Sam rate %.2f" % (f["nightly_low"] * 0.9)
    else:
        g = gateways.gateways(lat, lng)
        if g:
            why = "gateway: " + ", ".join("%s %.0f km" % (n, k) for k, _, n in g[:2])
        elif trips.campground_references(i):
            why = "family stayed here"
    if why:
        gate_kept[i] = why
    else:
        drops[i] = ("over the %s gate: base %s %s (%s); no gateway within 40 km, no named exception"
                    % (f["currency"], f["currency"], f["nightly_low"], src.split(" ('")[0]))

fns = {}
for i, (f, src) in prices.items():
    if i in drops:
        continue
    def fn(e, f=f, src=src):
        cs.apply_update(e, {"fees": f, cs.PROVENANCE: {**(e.get(cs.PROVENANCE) or {}),
                                                       "fees": {"source": src, "checked": TODAY}}})
        return e
    fns[i] = fn
for i, (spec, u, q) in mins.items():
    if i in drops:
        continue
    ms = []
    for p in spec.split(","):
        x = p.split(":"); r = {"nights": int(x[0]), "applies": x[1]}
        if len(x) > 2:
            r["season"] = x[2]
        ms.append(r)
    def mf(e, ms=ms, u=u, q=q, prev=fns.get(i)):
        if prev:
            e = prev(e)
        b = e.get("booking") or {}
        b["min_stay"] = ms
        e["booking"] = b
        e.setdefault(cs.PROVENANCE, {})["booking"] = {"source": f"{u} ('{q}', read 2026-10-16)", "checked": TODAY}
        return e
    fns[i] = mf
for i in drops:
    fns[i] = lambda e: None

print(f"{name}: priced {len([i for i in prices if i not in drops])}, minimums {len(mins)}, "
      f"dropped {len(drops)}, kept over gate {len(gate_kept)}, skipped {len(skips)}")
for i, w in drops.items():
    print("  DROP", i, cg[i]["name"], "|", w[:140])
for i, w in gate_kept.items():
    print("  KEEP", i, cg[i]["name"], prices[i][0]["nightly_low"], "|", w)
if APPLY:
    with open(f"{PR}/dropped_2026-10-19.jsonl", "a") as log:
        for i, w in drops.items():
            e = cg[i]
            log.write(json.dumps({"id": i, "name": e["name"], "state": e["state"], "ownership": e["ownership"],
                                  "action": "removed", "why": w}, ensure_ascii=False) + "\n")
    edit(fns, note_rescanned=False)
    json.dump({str(k): v for k, v in skips.items()}, open(f"{D}/left_{name}.json", "w"), indent=1, ensure_ascii=False)
    print("applied")
