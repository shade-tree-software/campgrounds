#!/usr/bin/env python3
"""Re-read matched Campendium pages for the FULL hrefs of the listing's outside links (the visible text is
only a bare domain, which loses a Google Sites or tourism-listing path). Writes 'hrefs' into CPD.jsonl."""
import html, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpd_read as cr
NOISE = re.compile(r"campendium|roadtrippers|onelink|apple\.com|play\.google|instagram|twitter|x\.com|youtube|"
                   r"tiktok|pinterest|zendesk|openstreetmap|mapbox|google\.com/maps|cloudfront|amazonaws|gstatic", re.I)
path = sys.argv[1]
recs = [json.loads(l) for l in open(path)]
for r in recs:
    if not r.get("url") or "hrefs" in r:
        continue
    url, page = cr.fetch(r["url"]); time.sleep(cr.PAUSE)
    if not url:
        continue
    hs = []
    for h in re.findall(r'href="(https?://[^"]+)"', page):
        h = html.unescape(h)
        if not NOISE.search(h) and h not in hs:
            hs.append(h)
    r["hrefs"] = hs
    print(r["id"], hs, flush=True)
    with open(path + ".tmp", "w") as fh:
        for x in recs:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    os.replace(path + ".tmp", path)
