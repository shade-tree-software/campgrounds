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


# A price counts when what LABELS it names a single/standard campsite ("Single Site: $19",
# "Camping - $22") or what FOLLOWS it does ("$28 fee per site for overnight camping",
# "$20 for a single site", "$22 a night"). The exclusion is applied to the label and to
# the following phrase only - never to the whole segment, where "(2 vehicles included
# per site)" after a real site price used to reject it.
LABEL = re.compile(r"(single|standard|individual|family|campsite|\bsite|camping|overnight)[^$]{0,40}$", re.I)
AFTER = re.compile(r"^\$\s?\d+(?:\.\d\d)?\s*(?:nightly\s+)?(?:fee\s+)?(?:per|/|a|for\s+a)\s*"
                   r"(?:single\s+)?(?:site|night|campsite|camping unit|unit)\b[^.$]{0,30}", re.I)
NOT_SINGLE = re.compile(r"double|triple|group|multi|equestrian|horse|cabin|walk|vehicle|day use|day-use|"
                        r"per day|per person|boat|overflow|firewood|parking", re.I)
ADDON = re.compile(r"holiday|additional|extra|hook-?up fee", re.I)
EXTRA_VEHICLE = re.compile(r"(extra|additional|second|2nd|third)\s+(\w+\s+)?vehicle", re.I)
INCLUDED = re.compile(r"includ\w*[^.$]*?vehicles?|vehicles?[^.$]*?included", re.I)
PRICE = re.compile(r"\$\s?(\d+(?:\.\d\d)?)")


def parse(block):
    """(low, high) from a fee block, or None when it needs a human."""
    if not block:
        return None
    body = block.replace("\xa0", " ").split("| Pet Information")[0].split("| Current Conditions")[0]
    body = body.split("| Getting There")[0].split("| Office Contact")[0][:600]
    body = re.split(r"discount(?:ed)? fees? (?:are|is)", body, flags=re.I)[0]   # pass-holder prices
    vals = []
    newer = re.search(r"\b202[6-9]\b", body)
    for seg in re.split(r"[|;]", body):
        if newer and re.search(r"\b20(1\d|2[0-5])\b", seg):
            continue                    # "2024 & 2025 $20 ...; In 2026 fee raises to $25" - last year's
        for m in PRICE.finditer(seg):
            label = seg[:m.start()].split(",")[-1].split(". ")[-1]
            if "$" in label:
                label = ""              # "$25 ... for single site and $50 per night for double site"
            if NOT_SINGLE.search(label) or ADDON.search(label):
                continue                # "Additional Vehicle Fee: $5 per night", "Walk-In Site: $40"
            # what follows the price, up to the next price or sentence: "$5/Night for extra vehicle";
            # "..., which includes two vehicles" is not a vehicle fee
            rest = INCLUDED.sub("", seg[m.start():].split("$")[1].split(". ")[0])
            if LABEL.search(label):
                # a labelled site price may be per vehicle ("Single Site: $8 per vehicle per
                # night"); only an add-on vehicle fee after it disqualifies it
                if not EXTRA_VEHICLE.search(rest):
                    vals.append(float(m.group(1)))
            elif AFTER.match(seg[m.start():]) and not (NOT_SINGLE.search(rest) or ADDON.search(rest)
                                                       or "max people" in rest):
                vals.append(float(m.group(1)))
    if vals:
        return min(vals), max(vals)
    if re.search(r"no fees? (are )?required|\bno fees?\b|free of charge", body, re.I) and "$" not in body:
        return 0.0, 0.0
    return None


# Read by hand (2026-10-10): the block contradicts itself or quotes a superseded price.
OVERRIDE = {
    6266: None,   # Whitetail: "Single site: $7", "$12.00 daily fee per single site" and "$25.00 per night"
    12216: (20, 20),   # Oak Flat: "Single Site: $5" is stale - "Fee increased to $20 ... on May 1, 2025"
}


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
        pr = OVERRIDE[r["id"]] if r["id"] in OVERRIDE else parse(c["block"])
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
