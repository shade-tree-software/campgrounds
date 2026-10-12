"""NJ Outdoors (njportal.com) site list of each park an unpriced NJ state entry links to:
every site's type, area, access and resident / non-resident cost, counted by (type, cost).

    python3 -I nj_sites.py OUT.json"""
import collections, html, json, os, re, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def lines(url):
    t = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style|noscript).*?</\1>", "", t)
    t = re.sub(r"(?i)<(br|p|li|tr|h\d|div|table|ul|section|dt|dd)[^>]*>", "\n", t)
    t = re.sub(r"(?i)</t[dh]>", " | ", t)
    return [l for l in (re.sub(r"\s+", " ", x).strip() for x in html.unescape(re.sub(r"<[^>]+>", " ", t)).split("\n")) if l]


rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
out = {}
for e in rows:
    if e.get("state") != "NJ" or e.get("ownership") != "state" or e.get("fees"):
        continue
    m = re.search(r"njportal\.com/DEP/NJOutdoors/Park/Details\?locationId=(\d+)", e.get("website") or "")
    if not m:
        continue
    url = m.group(0)
    L = lines("https://www." + url)
    recs, cur = [], None
    for l in L:
        if l.endswith(" |") and not l.startswith(("Cost", "Site", "Area", "Toilets")):
            cur = {"type": l[:-2].strip()}
            recs.append(cur)
        elif cur is not None and ":" in l:
            k, v = l.split(":", 1)
            if k in ("Site", "Area", "Site Access", "Cost", "Toilets", "Maximum People"):
                cur.setdefault(k, v.strip())
    c = collections.Counter((r.get("type"), r.get("Area"), r.get("Site Access"), r.get("Cost")) for r in recs if r.get("Cost"))
    out[e["id"]] = {"name": e["name"], "url": "https://www." + url,
                    "counts": [[*k, n] for k, n in sorted(c.items(), key=lambda kv: -kv[1])],
                    "electric_lines": [l for l in L if "lectric" in l][:12]}
    print(e["id"], e["name"]); [print("   ", n, k) for k, n in c.most_common()]
    time.sleep(1)
json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
