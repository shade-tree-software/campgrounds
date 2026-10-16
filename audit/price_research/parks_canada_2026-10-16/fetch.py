#!/usr/bin/env python3
"""Parks Canada campground fees from each park's own fees page (2026-10-16).

    python3 -I fetch.py IDS.json OUT.json

Every park publishes <park>/visit/tarifs-fees with a CAMPING table ("Tunnel Mountain -
Electrical | $ 40.00"). This caches the CAMPING-section text per park; the per-campground
rows are read by hand in build.py.
"""
import html, json, re, sys, time, urllib.request
ROOT = __file__.rsplit("/audit/", 1)[0]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/140"}
ids = set(json.load(open(sys.argv[1])))
rows = [r for r in json.load(open(ROOT + "/campgrounds.json")) if r["id"] in ids
        and "parks.canada.ca" in (r.get("website") or "")]
parks = {}
for r in rows:
    m = re.search(r"https://parks\.canada\.ca/((?:pn-np|lhn-nhs)/[a-z]{2}/[a-z\-]+)", r["website"])
    parks.setdefault(m.group(1), []).append(r["id"])
out = {}
for p, pid in parks.items():
    u = f"https://parks.canada.ca/{p}/visit/tarifs-fees"
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "ignore")
    except Exception as e:
        out[p] = {"url": u, "ids": pid, "error": str(e)}
        continue
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", t)))
    t = re.sub(r"(\|\s*)+", "| ", t).replace("| * ", "")
    i = t.find("| CAMPING |")
    j = t.find("div.wb-tabs")
    out[p] = {"url": u, "ids": pid, "camping": t[i:j] if i >= 0 else None,
              "modified": (re.findall(r"Date modified : \| (\d{4}-\d\d-\d\d)", t) or [None])[0]}
    time.sleep(1)
json.dump(out, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
print(len(out), "parks;", sum(1 for v in out.values() if v.get("camping")), "with a CAMPING table")
