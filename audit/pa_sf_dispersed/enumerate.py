#!/usr/bin/env python3
"""Every reservable PA state forest campsite on ReserveAmerica (2026-10-10).

DCNR's designated motorized/roadside state forest campsites are booked one site at
a time through pennsylvaniastateparks.reserveamerica.com, one "park" per forest.
Each campsiteDetails page carries the site's GPS, Type, Max Vehicle Length and
Site Access, which is what the gap check needs.

    python3 audit/pa_sf_dispersed/enumerate.py [OUT.jsonl]

Resumable: sites already in OUT are skipped.
"""
import html, json, os, re, sys, time, urllib.request, http.cookiejar

HOST = "https://pennsylvaniastateparks.reserveamerica.com"
FORESTS = {880251: "Delaware", 880252: "Pinchot", 880253: "Weiser", 880254: "Loyalsock",
           880255: "Moshannon", 880256: "Sproul", 880257: "Tiadaghton", 880258: "Elk",
           880259: "Susquehannock", 880260: "Tioga", 880261: "Tuscarora", 880263: "Buchanan",
           880264: "Rothrock", 880266: "Bald Eagle", 880267: "Forbes", 880268: "Clear Creek",
           880269: "Cornplanter", 883550: "Michaux"}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
op.addheaders = [("User-Agent", UA)]


def fetch(url):
    for attempt in range(4):
        try:
            return op.open(url, timeout=60).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(url)


def lines(raw):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S | re.I)
    t = re.sub(r"<(br|p|li|tr|td|th|h\d|div)[^>]*>", "\n", t, flags=re.I)
    return [re.sub(r"\s+", " ", l).strip()
            for l in html.unescape(re.sub(r"<[^>]+>", " ", t)).split("\n") if l.strip()]


def site_ids(pid):
    ids, start = [], 0
    while True:
        page = (f"{HOST}/campsiteSearch.do?contractCode=PA&parkId={pid}" if start == 0 else
                f"{HOST}/campsiteCalendar.do?page=calendar&contractCode=PA&parkId={pid}"
                f"&calarvdate=null&sitepage=true&startIdx={start}")
        raw = fetch(page)
        new = [i for i in dict.fromkeys(re.findall(r"siteId=(\d+)", raw)) if i not in ids]
        if not new:
            return ids
        ids += new
        L = lines(raw)
        tot = re.search(r"of\s+(\d+)", " ".join(l for l in L if "Search Results" in l) or "of 0")
        start += 25
        if not tot or start >= int(tot.group(1)):
            return ids
        time.sleep(0.5)


def details(pid, sid):
    L = lines(fetch(f"{HOST}/campsiteDetails.do?contractCode=PA&parkId={pid}&siteId={sid}"))
    d = {}
    for l in L:
        m = re.match(r"([A-Za-z][^:]{1,60}):\s*(.*)$", l)
        if m and m.group(1) not in d:
            d[m.group(1).strip()] = m.group(2).strip()
    return d


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "ra_sites.jsonl")
    done = set()
    if os.path.exists(out):
        done = {(r["park_id"], r["site_id"]) for r in map(json.loads, open(out))}
    with open(out, "a") as fh:
        for pid, forest in FORESTS.items():
            ids = site_ids(pid)
            print(f"{forest}: {len(ids)} sites", flush=True)
            for sid in ids:
                if (pid, sid) in done:
                    continue
                d = details(pid, sid)
                fh.write(json.dumps({"park_id": pid, "forest": forest, "site_id": sid, **d},
                                    ensure_ascii=False) + "\n")
                fh.flush()
                time.sleep(0.3)


if __name__ == "__main__":
    main()
