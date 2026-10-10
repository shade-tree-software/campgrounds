#!/usr/bin/env python3
"""Print the 'Site Type / Nightly/Daily Rates' table a classic ReserveAmerica
campground page carries (2026-10-10). Plain urllib - RA serves it without a browser.

    python3 audit/price_research/ra_rate_table.py URL [URL ...]

URL is a campgroundDetails.do link; host, contractCode and parkId are read off it.
Also prints the reservation-fee sentence from the policy text.
"""
import html, re, sys, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def text(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<(br|p|li|tr|td|th|h\d|div)[^>]*>", "\n", t, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return [l.strip() for l in t.split("\n") if l.strip()]


for url in sys.argv[1:]:
    print("=====", url)
    try:
        L = text(url)
    except Exception as e:
        print("ERR", e)
        continue
    try:
        i = next(k for k, l in enumerate(L) if l.startswith("Nightly/Daily Rates"))
        j = next(k for k in range(i, len(L)) if L[k].startswith("*Displayed rates"))
        print(" | ".join(L[i + 1:j]))
    except StopIteration:
        print("no rate table")
    for l in L:
        if re.search(r"reservation fee", l, re.I) and "$" in l:
            print("  FEE:", l[:220])
            break
