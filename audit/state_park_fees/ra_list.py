"""Every site of a classic ReserveAmerica park from its search listing (25 per page):
site id, loop, type, max people, equipment length, amenity flags. Writes JSON to stdout."""
import html, json, re, sys, time, urllib.request, http.cookiejar
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
def opener():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    return op
def rows(t):
    out = []
    for blk in t.split("<div class='br'>")[1:]:
        m = re.search(r"siteId=(\d+)", blk)
        if not m: continue
        cells = [' '.join(html.unescape(c).split()) for c in re.findall(r"<div class='td[^']*'>([^<]*)</div>", blk)]
        alts = re.findall(r"alt='([^']*)'", blk)
        name = re.search(r"aria-label='Site: ([^']*)'", blk)
        out.append({"siteId": m.group(1), "site": name.group(1) if name else None, "cells": cells,
                    "amenities": [a for a in alts if ' - ' in a or a in ('Near Water',)]})
    return out
def park(url):
    op = opener(); g = lambda u: op.open(u, timeout=60).read().decode("utf-8", "replace")
    host = re.match(r"https?://[^/]+", url).group(0)
    cc = re.search(r"contractCode=(\w+)", url).group(1); pid = re.search(r"parkId=(\d+)", url).group(1)
    g(f"{host}/campgroundDetails.do?contractCode={cc}&parkId={pid}")
    allrows, seen, start = [], set(), 0
    t = g(f"{host}/campsiteSearch.do?contractCode={cc}&parkId={pid}")
    while True:
        new = {}
        for r in rows(t):
            # A page carries each site twice (list row + calendar row); keep the list row,
            # whose second cell is the site type rather than an availability letter.
            if r["siteId"] in seen: continue
            if r["siteId"] not in new or (len(r["cells"]) > 1 and len(r["cells"][1]) > 2):
                new[r["siteId"]] = r
        if not new: break
        for sid, r in new.items(): seen.add(sid); allrows.append(r)
        start += 25
        if start > 2000: break
        time.sleep(0.3)
        t = g(f"{host}/campsitePaging.do?contractCode={cc}&parkId={pid}&startIdx={start}")
    return {"url": url, "host": host, "contract": cc, "parkId": pid, "sites": allrows}
if __name__ == "__main__":
    print(json.dumps(park(sys.argv[1])))
