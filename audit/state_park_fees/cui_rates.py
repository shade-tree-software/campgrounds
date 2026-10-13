"""Nightly prices of ReserveAmerica 'CUI' sites listed by cui_sites.py (2026-10-12).

    python3 -I cui_rates.py MM/DD/YYYY,MM/DD/YYYY SITES.jsonl > OUT.jsonl

A site page given a date (/camping/<slug>/r/campsiteDetails.page?parkID=&siteID=&arvdate=MM/DD/YYYY&lengthOfStay=1)
prints 'Camping Fees (1 Night)' / '$41.00 /Per Night $287.00 /Per Week' even beyond the booking window, and the site's
details: 'Loop: ...', 'Site Type: ...', then label / value line pairs ('Maximum Vehicle Length:' / '27', 'Driveway
Entry:', hookups). Where the map gave each site's loop, up to two sites of each loop and site type are priced on the
first date and one on the second (a site with no price that day is replaced by the next, up to four tries); for an
SVG-map park, whose map names no loop, every site is read on the first date, then one per loop and type on the second.
Tent, cabin, yurt, group and picnic-area types are skipped. One JSON line per site and date."""
import html, json, re, sys, time, urllib.request, http.cookiejar
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
SKIP = re.compile(r"(?i)tent|cabin|yurt|group|picnic|shelter|lodge|teepee|tipi")
dates = sys.argv[1].split(",")


def lines(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<(br|p|li|tr|td|th|h\d|div|span)[^>]*>", "\n", t, flags=re.I)
    return [re.sub(r"\s+", " ", l).strip() for l in html.unescape(re.sub(r"<[^>]+>", " ", t)).split("\n") if l.strip()]


def read(op, host, site, d):
    url = host + site["action"].split("&isSiteSpecificGroup")[0] + f"&arvdate={d}&lengthOfStay=1"
    L = lines(op.open(url, timeout=60).read().decode("utf-8", "replace"))
    k = next((j for j, l in enumerate(L) if l.startswith("Camping Fees")), None)
    rec = {"price": next((l for l in L[k + 1:k + 3] if "$" in l), None) if k is not None else None}
    for j, l in enumerate(L[:-1]):
        if l.startswith("Loop: ") and "loop" not in rec:
            rec["loop"] = l[6:].strip()
        elif l.startswith("Site Type: ") and "siteType" not in rec:
            rec["siteType"] = l[11:].strip()
        elif l.endswith(":") and len(l) < 40 and l[:-1] not in rec and not L[j + 1].endswith(":"):
            rec[l[:-1]] = L[j + 1]
    return rec


for line in open(sys.argv[2], encoding="utf-8"):
    park = json.loads(line)
    if park.get("error") or not park.get("sites"):
        continue
    host = re.match(r"https?://[^/]+", park["url"]).group(0)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    op.open(park["url"], timeout=60).read()
    cand = [s for s in park["sites"] if not SKIP.search(s.get("type") or "") and not SKIP.search(s.get("loop") or "")]

    def emit(s, d, r):
        print(json.dumps({"parkId": park["parkId"], "park": park.get("name"), "siteId": s["siteId"], "site": s["site"],
                          "loop": r.get("loop") or s.get("loop"), "type": s.get("type"), "date": d, **r}), flush=True)

    if park.get("map") == "svg":
        groups = {}
        for s in cand:
            time.sleep(0.4)
            try:
                r = read(op, host, s, dates[0])
            except Exception as x:  # noqa: BLE001 - one bad page shouldn't stop the run
                r = {"error": str(x)}
            emit(s, dates[0], r)
            if r.get("price"):
                groups.setdefault((r.get("loop"), s["type"]), s)
        for s in groups.values():
            for d in dates[1:]:
                time.sleep(0.4)
                try:
                    emit(s, d, read(op, host, s, d))
                except Exception as x:  # noqa: BLE001
                    emit(s, d, {"error": str(x)})
        continue
    groups = {}
    for s in cand:
        groups.setdefault((s.get("loop"), s.get("type")), []).append(s)
    for (loop, t), members in sorted(groups.items(), key=str):
        for di, d in enumerate(dates):
            want, tries, got = (2 if di == 0 else 1), 0, 0
            for s in members:
                if got >= want or tries >= 4 + want:
                    break
                tries += 1
                time.sleep(0.4)
                try:
                    r = read(op, host, s, d)
                except Exception as x:  # noqa: BLE001
                    r = {"error": str(x)}
                if not r.get("price"):
                    continue
                emit(s, d, r)
                got += 1
