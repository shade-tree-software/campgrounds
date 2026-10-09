#!/usr/bin/env python3
"""Nightly fees for Forest Service campgrounds from each fs.usda.gov page (2026-10-09).

    python3 audit/price_research/fs_fees.py --fetch [--limit N]   # cache fee blocks (1 s/request)
    python3 audit/price_research/fs_fees.py --build OUT.json      # findings for apply.py, free
    python3 audit/price_research/fs_fees.py --show                # print every cached fee block

Every fs.usda.gov campground page carries a "Fee Site and Info" block:
"Overnight Use: Single Site: $19 per night", or "No fees are required for this site".

- The URL is the entry's own `website` when it names a campground page
  (/rNN/<forest>/recreation/<slug>); when it only names the forest, the slug is
  guessed from the entry's name ("North Fork Poudre Campground" ->
  north-fork-poudre-campground) and a 404 is simply recorded.
- Only SINGLE (standard) site prices count; double, triple, group and multi-family
  sites price something else. Several single-site prices (electric vs not, or
  by season) become nightly_low / nightly_high.
- "No fee(s)" / "free of charge" in the block, with no single-site price -> 0 / 0.
- Anything else is left for a human: --show prints the blocks that did not parse.

Entries: federal, no `fees`, no recreation.gov campground link (those go through
recgov_rates.py), website on fs.usda.gov. Cache: trip_data/fs_fees.json (gitignored).
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, "trip_data", "fs_fees.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0"
PAGE = re.compile(r"(https?://(?:www\.)?fs\.usda\.gov/r\d\d/[a-z0-9\-]+/recreation/[a-z0-9\-]+)")
FOREST = re.compile(r"(https?://(?:www\.)?fs\.usda\.gov/r\d\d/[a-z0-9\-]+)")


def slug(name):
    s = re.sub(r"\(.*?\)", "", name.lower()).replace("&", "and").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s if s.endswith("campground") else s + "-campground"


def url_for(entry):
    web = entry.get("website") or ""
    m = PAGE.search(web)
    if m and not m.group(1).rstrip("/").endswith("/recreation"):
        return m.group(1)
    m = FOREST.search(web)
    return f"{m.group(1)}/recreation/{slug(entry['name'])}" if m else None


def targets():
    rows = json.load(open(os.path.join(ROOT, "campgrounds.json")))
    out = []
    for r in rows:
        if r.get("kind") == "family" or r.get("ownership") != "federal" or r.get("fees"):
            continue
        if "recreation.gov/camping" in (r.get("website") or ""):
            continue
        u = url_for(r)
        if u:
            out.append((r, u))
    return out


def fee_block(page):
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", page)))
    t = re.sub(r"(\|\s*)+", "| ", t)
    i = t.find("Fee Site and Info")
    if i < 0:
        i = t.find("| Fees |")
    if i < 0:
        return None
    return t[i:i + 700]


def fetch(limit):
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [u for _, u in targets() if u not in cache]
    todo = list(dict.fromkeys(todo))
    if limit:
        todo = todo[:limit]
    for n, u in enumerate(todo, 1):
        try:
            page = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}),
                                          timeout=30).read().decode("utf-8", "ignore")
            cache[u] = {"status": 200, "block": fee_block(page)}
        except urllib.error.HTTPError as e:
            cache[u] = {"status": e.code, "block": None}
        except Exception as e:
            print("ERR", u, str(e)[:80])
            continue
        with open(CACHE + ".tmp", "w") as fh:
            json.dump(cache, fh)
        os.replace(CACHE + ".tmp", CACHE)
        if n % 50 == 0:
            print(n, "of", len(todo))
        time.sleep(1.0)
    print("cached", len(cache))


SINGLE = re.compile(r"(?:Single|Standard|Individual|Family|Campsite|Site)[^|$]{0,40}?:?\s*\$\s?(\d+(?:\.\d\d)?)", re.I)
NOT_SINGLE = re.compile(r"double|triple|group|multi|equestrian|horse|cabin|extra vehicle|day use|day-use", re.I)


def parse(block):
    """(low, high) from a fee block, or None when it needs a human."""
    if not block:
        return None
    body = block.split("| Pet Information")[0].split("| Current Conditions")[0][:600]
    vals = []
    for seg in re.split(r"\|", body):
        if NOT_SINGLE.search(seg):
            continue
        vals += [float(v) for v in SINGLE.findall(seg)]
    if vals:
        return min(vals), max(vals)
    if re.search(r"no fees? (are )?required|\bno fees?\b|free of charge", body, re.I) and "$" not in body:
        return 0.0, 0.0
    return None


def build(out):
    cache = json.load(open(CACHE))
    F, unparsed, missing = [], 0, 0
    for r, u in targets():
        c = cache.get(u)
        if not c:
            continue
        if c["status"] != 200 or not c["block"]:
            missing += 1
            continue
        pr = parse(c["block"])
        if not pr:
            unparsed += 1
            continue
        lo, hi = (int(v) if float(v).is_integer() else v for v in pr)
        fees = {"nightly_low": lo, "nightly_high": hi}
        if hi:
            fees["currency"] = "USD"
        quote = re.sub(r"\s+", " ", c["block"].split("| Pet Information")[0])[:220]
        F.append({"id": r["id"], "fees": fees, "source": f"{u} ('{quote}')"})
    json.dump(F, open(out, "w"), indent=1, ensure_ascii=False)
    print(len(F), "findings;", unparsed, "blocks need a human;", missing, "pages missing/404")


def show():
    cache = json.load(open(CACHE))
    for r, u in targets():
        c = cache.get(u)
        if c and c["block"] and not parse(c["block"]):
            print(r["id"], r["name"], "|", u, "\n   ", c["block"][:400])


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch(int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0)
    elif "--build" in sys.argv:
        build(sys.argv[sys.argv.index("--build") + 1])
    elif "--show" in sys.argv:
        show()
