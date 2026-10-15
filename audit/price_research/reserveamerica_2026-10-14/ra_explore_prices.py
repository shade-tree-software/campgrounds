#!/usr/bin/env python3
"""Per-site-type nightly prices off a new-style ReserveAmerica "explore" page (2026-10-14).

The explore pages and their JSON API sit behind an AWS WAF challenge, so this
drives the one shared browser (audit/private_gap_browser/drv.py). It walks the
park's campsites table, keeps one site of each site type (cabins, groups and
the like skipped), and reads each one's 'PRICE BREAKDOWN: Camping Fees (1 night)'
on the given arrival dates.

    python3 ra_explore_prices.py OUT.jsonl ID=EXPLORE_URL [ID=EXPLORE_URL ...] [--dates 2027-06-15,2027-06-19]
"""
import json, re, subprocess, sys, time

FALLBACK = ["2026-10-28"]  # tried only when no main date priced
DRV = "audit/private_gap_browser/drv.py"
SKIP = re.compile(r"(?i)shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|equest|tent only|walk.?in|hike")


def drv(*a):
    return subprocess.run(["python3", DRV, *a], capture_output=True, text=True, timeout=180).stdout


ROWS = ("JSON.stringify([...document.querySelectorAll('tr')].map(r=>[[...r.querySelectorAll('td')].map(c=>c.innerText.replace(/\\s+/g,' ').trim()),"
        "[...r.querySelectorAll('a')].map(a=>a.href).filter(h=>h.includes('campsite-booking'))[0]]).filter(x=>x[1]))")


def main():
    args = sys.argv[1:]
    dates = ["2027-06-15", "2027-06-19"]
    if "--dates" in args:
        k = args.index("--dates"); dates = args[k + 1].split(","); del args[k:k + 2]
    out = open(args[0], "a", encoding="utf-8")
    for spec in args[1:]:
        cid, url = spec.split("=", 1)
        base = re.sub(r"/(overview|campsites|campsite-availability)?$", "", url.split("?")[0])
        rec = {"id": int(cid), "url": base, "types": {}, "prices": []}
        for page in range(0, 12):
            drv("goto", f"url={base}/campsites" + (f"?pageNumber={page}" if page else ""), "wait=7000")
            rows = []
            for _ in range(4):
                try:
                    rows = json.loads(drv("eval", f"js={ROWS}"))
                except ValueError:
                    rows = []
                if rows:
                    break
                time.sleep(4)
            new = 0
            for cells, href in rows:
                t = cells[2] if len(cells) > 2 else "?"
                rec["types"].setdefault(t, [])
                if href not in rec["types"][t]:
                    rec["types"][t].append(href); new += 1
            if not rows or not new or len(rows) < 20:
                break
        for t, hrefs in rec["types"].items():
            if SKIP.search(t):
                continue
            got = False
            for dt in dates + FALLBACK:
                if got and dt in FALLBACK:
                    break
                drv("goto", f"url={hrefs[0]}?arrivalDate={dt}&lengthOfStay=1", "wait=7000")
                txt = drv("text", "mx=6000")
                m = re.search(r"Camping Fees \(1 night\)\s*\n\s*(\$[\d.,]+[^\n]*)", txt)
                eq = re.search(r"(?i)equipment length[^\n]*\n([^\n]*)", txt)
                rec["prices"].append({"type": t, "site": hrefs[0], "date": dt, "price": m.group(1) if m else None,
                                      "length": eq.group(1)[:60] if eq else None})
                got = got or bool(m)
                print(cid, t[:40], dt, m.group(1) if m else None, flush=True)
        rec["types"] = {t: len(h) for t, h in rec["types"].items()}
        out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()


main()
