#!/usr/bin/env python3
"""Nightly prices per site type off Campspot (2026-10-10).

Loads each park page in the shared one-browser driver (drv_server.py must be
running) and reads the availability JSON the page itself fetches
(/api/gator-core/v2/availability/parks/<id>); called directly from curl or a
page-context fetch it is refused. Keeps RV categories only.

    python3 audit/price_research/campspot_prices.py LIST.tsv OUT.jsonl [DATE ...]

LIST.tsv rows are `id<TAB>slug`; DATE is a check-in (one-night stays).
"""
import datetime, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DRV = os.path.join(HERE, "..", "private_gap_browser", "drv.py")


def d(*args):
    return subprocess.run([sys.executable, DRV, *args], capture_output=True, text=True).stdout


def main():
    rows = [l.split("\t")[:2] for l in open(sys.argv[1]).read().split("\n") if l.strip()]
    out = open(sys.argv[2], "a")
    dates = sys.argv[3:] or ["2026-11-10", "2027-06-15", "2027-06-19"]
    for eid, slug in rows:
        for ci in dates:
            co = (datetime.date.fromisoformat(ci) + datetime.timedelta(days=1)).isoformat()
            d("goto", f"url=https://www.campspot.com/park/{slug}?checkin={ci}&checkout={co}&guests=2,0,0",
              "wait=9000")
            hits = [l for l in d("net", "grep=availability/parks", "last=400").splitlines()
                    if " 200 " in l and f"checkin={ci}" in l]
            rec = {"id": int(eid), "slug": slug, "checkin": ci, "types": []}
            if hits:
                body = d("body", "max=5000000", "i=" + re.match(r"\[(\d+)\]", hits[-1]).group(1))
                try:
                    for c in json.loads(body):
                        lens = [((s.get("rvInfo") or {}).get("rvLengthMax")) for s in c.get("campsites", [])]
                        rec["types"].append({
                            "name": c.get("name"), "cat": c.get("campsiteCategoryCode"),
                            "price": c.get("averagePricePerNight"),
                            "max_len": max([x for x in lens if x] or [None]) if any(lens) else None,
                            "available": sum(s.get("availability") == "AVAILABLE" for s in c.get("campsites", [])),
                        })
                except ValueError:
                    rec["error"] = body[:200]
            else:
                rec["error"] = "no availability response"
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(eid, slug, ci, len(rec["types"]), rec.get("error", ""), flush=True)


main()
