"""Turn hand-read rows into findings, checking each quote really appears on a fetched page.
python3 -I build.py ST   reads rows_ST.txt, pages_ST.jsonl -> findings_ST.json
rows_ST.txt lines:  id | low | high | note | quote   (CAD for Canadian provinces; '#' comments; 'skip id reason' lines ignored)"""
import json, re, sys, os
st = sys.argv[1]; d = os.path.dirname(os.path.abspath(__file__))
CAD = {"AB","BC","MB","NB","NL","NS","ON","PE","QC","SK"}
pages = {}
for l in open(f"{d}/pages_{st}.jsonl"):
    r = json.loads(l); pages[r["id"]] = r["pages"]
norm = lambda s: re.sub(r"\s*\|\s*(\|\s*)*", " | ", re.sub(r"\s+", " ", s))
out, bad = [], []
for ln in open(f"{d}/rows_{st}.txt"):
    ln = ln.strip()
    if not ln or ln.startswith("#") or ln.startswith("skip"): continue
    i, lo, hi, note, q = [x.strip() for x in ln.split("|", 4)]
    i = int(i); hit = None
    for p in pages.get(i, []):
        if any(norm(q) in norm(x) for x in p.get("lines", [])): hit = p["url"]; break
    if not hit: bad.append(i); continue
    f = lambda v: float(v) if "." in v else int(v)
    out.append({"id": i, "fees": {"nightly_low": f(lo), "nightly_high": f(hi), "currency": "CAD" if st in CAD else "USD", "note": note},
                "source": f"{hit} ('{q}', read 2026-10-16)"})
json.dump(out, open(f"{d}/findings_{st}.json", "w"), indent=1, ensure_ascii=False)
print(st, len(out), "findings", "QUOTE NOT FOUND:" if bad else "", bad)
