"""The posted rate of each (loop, site type) of classic ReserveAmerica parks already listed by ra_list.py (2026-10-12).

    python3 -I ra_rate_card.py M/D/YYYY LISTING.json [LISTING.json ...] > OUT.jsonl

A site page for a date outside the booking window prints no 'Camping Fees (1 night)', but given a date it does print
the site's 'Price Rate:*' ('$35.00 Per Night , $245.00 Per Week'; '*Rate may vary across dates; displayed rates do not
reflect discounts, fees or taxes') - Saskatchewan's pages in October, for any 2027 date (no date: no rate line). For
each loop and site type (seasonal, group, shelter, yurt and other non-campsite types skipped), up to two sites are read:
the rate line and the site details (service, amps, hookups, max equipment length, access, allowed equipment). One JSON
line per site."""
import html, json, re, sys, time, urllib.request, http.cookiejar
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
SKIP = re.compile(r"(?i)seasonal|shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|"
                  r"equest|lean-to|meeting|swim|lesson|hall|tiny|bunk|room|double site")
KEYS = ("Type", "Site, Loop", "Service", "Electricity Hookup (Amps)", "Water Hookup", "Sewer Hookup", "Full Hookup",
        "Site Access", "Driveway Entry", "Site Length (ft)", "Maximum Equipment Length (ft)", "Allowed Equipment",
        "Site Reserve Type", "Looking For Category")


def lines(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<(br|p|li|tr|td|th|h\d|div)[^>]*>", "\n", t, flags=re.I)
    return [re.sub(r"\s+", " ", l).strip() for l in html.unescape(re.sub(r"<[^>]+>", " ", t)).split("\n") if l.strip()]


date = sys.argv[1]
for path in sys.argv[2:]:
    d = json.load(open(path))
    groups = {}
    for r in d["sites"]:
        t = r["cells"][1] if len(r["cells"]) > 1 else "?"
        if SKIP.search(t) or "host" in (r.get("site") or "").lower():
            continue
        groups.setdefault((r["cells"][0] if r["cells"] else "?", t), []).append(r)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    op.open(f"{d['host']}/campgroundDetails.do?contractCode={d['contract']}&parkId={d['parkId']}", timeout=60).read()
    for (loop, t), members in sorted(groups.items()):
        for r in members[:2]:
            time.sleep(0.5)
            rec = {"parkId": d["parkId"], "loop": loop, "type": t, "site": r["site"], "siteId": r["siteId"], "cells": r["cells"],
                   "date": date}
            try:
                L = lines(op.open(f"{d['host']}/campsiteDetails.do?contractCode={d['contract']}&parkId={d['parkId']}"
                                  f"&siteId={r['siteId']}&arvdate={date}&lengthOfStay=1", timeout=60).read().decode("utf-8", "replace"))
            except Exception as x:  # noqa: BLE001 - one bad page shouldn't stop the run
                rec["error"] = str(x)
                print(json.dumps(rec), flush=True)
                continue
            k = next((j for j, l in enumerate(L) if l.startswith("Price Rate")), None)
            rec["rate"] = next((l for l in L[k + 1:k + 3] if "$" in l), None) if k is not None else None
            notes = [L[j + 1] for j, l in enumerate(L[:-1]) if l == "Area" and j + 1 < len(L) and L[j + 1] not in ("Notes", "Area")]
            if notes:
                rec["area_notes"] = notes
            for line in L:
                if ":" in line:
                    kk, v = line.split(":", 1)
                    if kk.strip() in KEYS and kk.strip() not in rec:
                        rec[kk.strip()] = v.strip()
            print(json.dumps(rec), flush=True)
