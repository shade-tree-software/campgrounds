"""Set booking.min_stay from the operator's site.  python3 -I minstay.py ID=SPEC ...
SPEC: comma list of nights:applies[:season], e.g. 2:weekend,3:holiday  or 2:summer:June-September.
Refuses (prints SKIP) when the entry already carries a min_stay - those were set by hand from a source."""
import sys, json
sys.path.insert(0, __file__.rsplit("/private_2026-10-16/", 1)[0])
from edit_entries import edit
fns = {}
for a in sys.argv[1:]:
    i, spec = a.split("="); i = int(i); ms = []
    for p in spec.split(","):
        x = p.split(":"); r = {"nights": int(x[0]), "applies": x[1]}
        if len(x) > 2: r["season"] = x[2]
        ms.append(r)
    def f(e, ms=ms):
        b = e.get("booking") or {}
        if b.get("min_stay"):
            print("SKIP", e["id"], "already has", b["min_stay"]); return e
        b["min_stay"] = ms; e["booking"] = b
        e.setdefault("provenance", {})["booking"] = {"source": (e.get("website") or "").split()[0] + " (read 2026-10-16)", "checked": "2026-10-16"}
        print("SET", e["id"], ms); return e
    fns[i] = f
edit(fns)
