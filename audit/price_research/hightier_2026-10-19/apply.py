"""High-tier pricing pass (2026-10-19): apply one hand-read chunk.

    python3 -I apply.py NAME [--apply]        reads rows_NAME.txt; dry run without --apply

Same shape as ../private2_2026-10-19/run_chunk.py, but the rates here come from live booking
engines (KOA's form, Campspot's API ...) and fresh page reads rather than round 1's saved pages,
so each row carries its source instead of a quote to look up. rows_NAME.txt (split on ' | '):
    ID | LOW | HIGH | fees note | source       base rate before tax, CAD for provinces; HIGH '-' when unknown
    min ID | SPEC | source                     nights:applies[:season], comma-separated
    set ID | FIELD | VALUE                     identity fix (name / website / phone / note); '-' sets null
    keep / drop / skip ID | reason             as in run_chunk.py
The price gate and its exceptions are run_chunk.py's; drops are logged to ../dropped_2026-10-19.jsonl.
"""
import json, os, sys, datetime
D = os.path.dirname(os.path.abspath(__file__))
PR = os.path.dirname(D)
ROOT = os.path.dirname(os.path.dirname(PR))
sys.path[:0] = [ROOT, PR]
from edit_entries import edit           # noqa: E402
import campground_schema as cs          # noqa: E402
import gateways, trips                  # noqa: E402

name = sys.argv[1]; APPLY = "--apply" in sys.argv
CAD = {"AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK"}
LIMIT = {"USD": 50, "CAD": 69}
NAMED = {14435}  # Fort Myers ids and Liberty Harbor 3363 left 2026-10-21: covered by gateways.py (family homes; New York 3 km)
TODAY = datetime.date.today().isoformat()
cg = {e["id"]: e for e in json.load(open(f"{ROOT}/campgrounds.json"))}
num = lambda v: float(v) if "." in v else int(v)

prices, mins, sets, drops, skips, keeps = {}, {}, {}, {}, {}, {}
for ln in open(f"{D}/rows_{name}.txt"):
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    kind = ln.split()[0]
    if kind in ("drop", "skip", "min", "keep", "set"):
        parts = [x.strip() for x in ln[len(kind):].split("|", 2)]
        i = int(parts[0])
        if i not in cg:
            sys.exit(f"no entry {i}")
        if kind == "drop":
            drops[i] = parts[1]
        elif kind == "keep":
            keeps[i] = parts[1]
        elif kind == "skip":
            skips[i] = parts[1]
        elif kind == "set":
            sets.setdefault(i, {})[parts[1]] = None if parts[2] == "-" else parts[2]
        else:
            mins[i] = (parts[1], parts[2])
        continue
    i, lo, hi, note, src = [x.strip() for x in ln.split("|", 4)]
    i = int(i); e = cg[i]
    if (e.get("fees") or {}).get("nightly_low") is not None:
        print("ALREADY PRICED", i); continue
    cur = "CAD" if e["state"] in CAD else "USD"
    f = {"nightly_low": num(lo), "nightly_high": None if hi == "-" else num(hi), "currency": cur, "checked": "2026", "note": note}
    prices[i] = ({k: v for k, v in f.items() if v is not None}, src)

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
                    % (f["currency"], f["currency"], f["nightly_low"], src))

fns = {}
for i in set(prices) | set(mins) | set(sets):
    if i in drops:
        continue
    def fn(e, i=i):
        if i in sets:
            for k, v in sets[i].items():
                e[k] = v
        if i in prices:
            f, src = prices[i]
            cs.apply_update(e, {"fees": f, cs.PROVENANCE: {**(e.get(cs.PROVENANCE) or {}),
                                                           "fees": {"source": src, "checked": TODAY}}})
        if i in mins:
            spec, src = mins[i]
            ms = []
            for p in spec.split(","):
                x = p.split(":"); r = {"nights": int(x[0]), "applies": x[1]}
                if len(x) > 2:
                    r["season"] = x[2]
                ms.append(r)
            b = e.get("booking") or {}
            b["min_stay"] = ms
            e["booking"] = b
            e.setdefault(cs.PROVENANCE, {})["booking"] = {"source": src, "checked": TODAY}
        return e
    fns[i] = fn
for i in drops:
    fns[i] = lambda e: None

print(f"{name}: priced {len([i for i in prices if i not in drops])}, minimums {len(mins)}, "
      f"identity fixes {len(sets)}, dropped {len(drops)}, kept over gate {len(gate_kept)}, skipped {len(skips)}")
for i, w in drops.items():
    print("  DROP", i, cg[i]["name"], "|", w[:160])
for i, w in gate_kept.items():
    print("  KEEP", i, cg[i]["name"], prices[i][0]["nightly_low"], "|", w)
for i, s in sets.items():
    print("  SET ", i, cg[i]["name"], "|", {k: (v or "")[:60] for k, v in s.items()})
if APPLY:
    with open(f"{PR}/dropped_2026-10-19.jsonl", "a") as log:
        for i, w in drops.items():
            e = cg[i]
            log.write(json.dumps({"id": i, "name": e["name"], "state": e["state"], "ownership": e["ownership"],
                                  "action": "removed", "why": w}, ensure_ascii=False) + "\n")
    edit(fns, note_rescanned=True)
    json.dump({str(k): v for k, v in skips.items()}, open(f"{D}/left_{name}.json", "w"), indent=1, ensure_ascii=False)
    print("applied")
