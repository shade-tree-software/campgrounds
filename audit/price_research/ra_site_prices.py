#!/usr/bin/env python3
"""Per-site nightly prices off a classic ReserveAmerica campground (2026-10-10).

The campground page's rate table excludes hookup "attribute fees" (Beavers Bend
shows $18 for every type; an RV Premium site actually costs $40), so this reads
each site's 'Price Breakdown: Camping Fees (1 night)' instead - the KY recipe.

    python3 audit/price_research/ra_site_prices.py URL [--dates 6/15/2027,6/19/2027] [--per-type 2]

URL is any campgroundDetails.do / campsiteSearch.do link (host, contractCode,
parkId read off it). Lists every site (paged 25 at a time), keeps --per-type
sites of each site type, and prints type, site, date, price and electric.
"""
import html, os, re, sys, time, urllib.request, http.cookiejar

SKIP = re.compile(r"(?i)shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|equest")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
op.addheaders = [("User-Agent", UA)]


def lines(url):
    t = op.open(url, timeout=60).read().decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<(br|p|li|tr|td|th|h\d|div)[^>]*>", "\n", t, flags=re.I)
    return t, [re.sub(r"\s+", " ", l).strip() for l in html.unescape(re.sub(r"<[^>]+>", " ", t)).split("\n") if l.strip()]


def main():
    url = sys.argv[1]
    dates = ["10/20/2026", "6/15/2027", "6/19/2027"]
    per_type = 2
    if "--dates" in sys.argv:
        dates = sys.argv[sys.argv.index("--dates") + 1].split(",")
    if "--per-type" in sys.argv:
        per_type = int(sys.argv[sys.argv.index("--per-type") + 1])
    host = re.match(r"https?://[^/]+", url).group(0)
    cc = re.search(r"contractCode=(\w+)", url).group(1)
    pid = re.search(r"parkId=(\d+)", url).group(1)
    sites, start = {}, 0
    while True:
        page = (f"{host}/campsiteSearch.do?contractCode={cc}&parkId={pid}" if start == 0 else
                f"{host}/campsiteCalendar.do?page=calendar&contractCode={cc}&parkId={pid}"
                f"&calarvdate=null&sitepage=true&startIdx={start}")
        raw, L = lines(page)
        ids = list(dict.fromkeys(re.findall(r"siteId=(\d+)", raw)))
        new = [i for i in ids if i not in sites]
        if not new:
            break
        for i in new:
            sites[i] = None
        tot = re.search(r"of\s+(\d+)", " ".join(l for l in L if "Search Results" in l) or "of 0")
        start += 25
        if not tot or start >= int(tot.group(1)):
            break
        time.sleep(0.5)
    # Site type of every site, then per type keep trying sites until each date
    # has `per_type` prices (a booked night shows no price), capped at 10 sites.
    types = {}
    for sid in sites:
        _, L = lines(f"{host}/campsiteDetails.do?contractCode={cc}&parkId={pid}&siteId={sid}")
        typ = next((l.split(":", 1)[1].strip() for l in L if l.startswith("Type:")), "?")
        loop = next((l.split(":", 1)[1].strip() for l in L if l.startswith("Site, Loop:")), sid)
        types.setdefault(typ, []).append((sid, loop))
        time.sleep(0.2)
    print(f"# {len(sites)} sites; types: { {k: len(v) for k, v in types.items()} }")
    for typ, members in types.items():
        if SKIP.search(typ):
            continue
        got = {d: 0 for d in dates}
        for sid, loop in members[:10]:
            for d in dates:
                if got[d] >= per_type:
                    continue
                _, L = lines(f"{host}/campsiteDetails.do?contractCode={cc}&parkId={pid}&siteId={sid}"
                             f"&arvdate={d}&lengthOfStay=1")
                el = next((l.split(":", 1)[1].strip() for l in L if l.startswith("Electricity Hookup:")), "")
                pr = None
                # KY prints 'Camping Fees (1 night)' on one line; NY splits 'Use Fees' / '(1 night)'
                k = next((j for j, l in enumerate(L) if l in ("Camping Fees (1 night)", "Use Fees (1 night)")
                          or (l in ("Camping Fees", "Use Fees") and j + 1 < len(L) and L[j + 1] == "(1 night)")), None)
                if k is not None:
                    pr = next((l for l in L[k + 1:k + 4] if "$" in l), None)
                    rf = next((L[j + 1] for j in range(k, min(k + 12, len(L) - 1))
                               if L[j] == "Reservation Fees"), "")
                    if pr and rf:
                        pr += f" (reservation fee {rf})"
                if not pr and os.environ.get("RA_DEBUG"):
                    print("  DEBUG", loop, d, " / ".join(L[8:40])[:900])
                if pr:
                    got[d] += 1
                    print(f"{typ}\t{loop}\t{d}\t{pr}\t{el}", flush=True)
                time.sleep(0.2)
            if all(v >= per_type for v in got.values()):
                break
        if not any(got.values()):
            print(f"{typ}\t-\tno price on any date tried")

main()
