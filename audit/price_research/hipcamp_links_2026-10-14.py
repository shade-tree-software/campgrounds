"""Which of our Hipcamp links still sell anything (AWH 2026-10-14 #8: "Remove dead or unclaimed hipcamp links").

python3 -I hipcamp_links_2026-10-14.py OUT.json [--recheck] [--all-pages]

Hipcamp's sitemap is the oracle (feedback_require_live_web_presence): robots.txt -> sitemaps/v2/main.xml.gz -> one
us-lands-XX / ca-lands-XX file per state or province, listing only lands that can be booked, so a dormant listing
(status ASLEEP, isBookable false) is absent from it. A link is matched by its land id, the 8-character tail of the
slug, against every lands file (a listing filed under another state still counts). Each absent link's own page is
then read for what the absence means (--all-pages reads every link's page: the sitemap lags, so a live listing
can be missing from it): a redirect away from the listing, a 404, or the page's status and isBookable.
One record per link: {id, name, state, ownership, url, land, in_sitemap, page: {...}, other_links}.
"""
import gzip, json, os, re, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}
LAND = re.compile(r"hipcamp\.com/(?:[a-z]{2}-[A-Z]{2}/)?land/([a-z0-9-]+?)-([a-z0-9]{8})(?:[/?#]|$)")


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
        return r.geturl(), r.status, gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body


def records(node, land, found):
    if isinstance(node, dict):
        if node.get("maskedId") == land:
            found.append(node)
        for v in node.values():
            records(v, land, found)
    elif isinstance(node, list):
        for v in node:
            records(v, land, found)


def page(url, land):
    """The listing's own record, read from the page's __NEXT_DATA__ JSON. Answers vary from one fetch to the next:
    a 15 KB shell with no page data, or page data without the listing in it, are no answer, so ask again (up to 6
    times). A redirect to a /d/ state index is an answer: the listing is gone."""
    out = {}
    for attempt in range(6):
        try:
            final, status, body = get(url)
        except urllib.error.HTTPError as ex:
            return {"http": ex.code}
        out = {"http": status, "final": final, "tries": attempt + 1}
        if "/d/" in final:
            out["index"] = True
            return out
        t = body.decode("utf-8", "replace")
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', t, re.S)
        found = []
        if m:
            records(json.loads(m.group(1)), land, found)
        if found:
            rec = {}
            for r in found:  # the same land can appear as several partial objects; merge what they say
                for k in ("status", "fullName", "isBookable", "isPaused", "isDraft", "isExternal"):
                    if k in r and k not in rec:
                        rec[k] = r[k]
            out.update(rec)
            out["own_record"] = True
            return out
        time.sleep(4 * (attempt + 1))
    out["own_record"] = False
    return out


rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
links = []
for e in rows:
    ws = [w for w in (e.get("website") or "").split("\n") if w]
    for w in ws:
        if "hipcamp.com" in w:
            m = LAND.search(w)
            links.append({"id": e["id"], "name": e["name"], "state": e["state"], "ownership": e.get("ownership"),
                          "url": w, "land": m.group(2) if m else None,
                          "other_links": [x for x in ws if "hipcamp.com" not in x]})
print(len(links), "Hipcamp links on", len({x["id"] for x in links}), "entries")

lands = {}
_, _, idx = get("https://www.hipcamp.com/sitemaps/v2/main.xml.gz") if "--recheck" not in sys.argv else (0, 0, b"")
files = [u for u in re.findall(r"<loc>([^<]+)</loc>", idx.decode()) if re.search(r"/(us|ca)-lands-", u)]
for u in files:
    _, _, x = get(u)
    for loc in re.findall(r"<loc>([^<]+)</loc>", x.decode("utf-8", "replace")):
        m = LAND.search(loc)
        if m:
            lands[m.group(2)] = loc
    time.sleep(0.3)
print(len(files), "lands files,", len(lands), "lands")
RECHECK = set()
if "--recheck" in sys.argv:  # re-read the absent links' pages only, reusing OUT's sitemap answers
    prev = {(x["id"], x["url"]): x for x in json.load(open(sys.argv[1], encoding="utf-8"))}
    for x in links:
        x["in_sitemap"] = prev[(x["id"], x["url"])]["in_sitemap"]
        if not x["in_sitemap"]:
            RECHECK.add(x["id"])
for x in links:
    if "--recheck" not in sys.argv:
        x["in_sitemap"] = bool(x["land"] and x["land"] in lands)
    if "--all-pages" in sys.argv or (not x["in_sitemap"] and ("--recheck" not in sys.argv or x["id"] in RECHECK)):
        x["page"] = page(x["url"], x["land"])
        time.sleep(1.0)
    print(x["id"], x["ownership"], "IN " if x["in_sitemap"] else "OUT", x["url"][-60:], json.dumps(x.get("page"))[:200])
json.dump(links, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
