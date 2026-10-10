#!/usr/bin/env python3
"""Digest of fee text off mycountyparks.com parks (2026-10-10). Plain urllib.

    python3 audit/price_research/mycountyparks_fees.py LIST.tsv > digest.txt

LIST rows: id<TAB>state<TAB>name<TAB>url. For each park, fetches the park page
(the URL's /County/<c>/Park/<p> prefix), collects its Facility links, and prints
the distinct 'Fees' blocks and '$' lines found on up to 25 facility pages, with
the facility names that carry each, for a person to read.
"""
import html, re, sys, time, urllib.request
from collections import OrderedDict

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
BASE = "https://www.mycountyparks.com"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S | re.I)
    t = re.sub(r"<(br|p|li|tr|td|h\d|div)[^>]*>", "\n", t, flags=re.I)
    L = [re.sub(r"\s+", " ", l).strip() for l in html.unescape(re.sub(r"<[^>]+>", " ", t)).split("\n")]
    return raw, [l for l in L if l]


def fee_lines(L):
    out = []
    for i, l in enumerate(L):
        if l == "Fees":
            out += L[i + 1:i + 4]
        elif re.search(r"\$\s?\d", l) and len(l) < 400:
            out.append(l)
    return out


for row in open(sys.argv[1]).read().splitlines():
    eid, st, name, url = row.split("\t")[:4]
    print(f"##### {eid} {st} {name} | {url}", flush=True)
    m = re.search(r"(/County/[^/]+/Park/[^/?#]+)", url, re.I)
    try:
        raw, L = get(BASE + m.group(1) if m else url)
    except Exception as e:
        print("  ERR", e)
        continue
    facs = list(OrderedDict.fromkeys(
        f for f in re.findall(r'href="(/County/[^"]+/Facility/[^"/]+)', raw, re.I)))
    print(f"  {len(facs)} facilities")
    seen = OrderedDict()
    for l in fee_lines(L):
        seen.setdefault(l, ["park page"])
    for f in facs[:25]:
        try:
            _, FL = get(BASE + f)
        except Exception as e:
            continue
        for l in fee_lines(FL):
            seen.setdefault(l, []).append(f.rsplit("/", 1)[-1])
        time.sleep(0.3)
    for l, where in seen.items():
        if re.search(r"(?i)donat|gift|shelter|lodge|cabin|pavilion|application fee", l):
            continue
        print(f"  [{len(where)}x e.g. {where[0][:40]}] {l[:330]}")
