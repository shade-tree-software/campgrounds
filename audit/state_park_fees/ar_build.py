"""Arkansas State Parks findings: every campsite of each park's calendar on reserve.arkansasstateparks.com for two weeks
from 2026-10-13 and from 2027-06-15, with each site's attributes (ar_calendar.py -> ar_calendar_2026-10-12.json).

    python3 -I ar_build.py OUT

Arkansas publishes no rate table and prices each site and night by demand ('rates are subject to change based on
availability and season'; 'The quoted rate for each night does not include taxes or the reservation fee'), as South
Carolina, Alabama and Tennessee do on the same vendor's sites, so an entry carries the range of its cheapest kind of RV
site over every bookable night in the two windows, and the note gives each kind's range. RV sites are rows typed
rv-tent with a max RV length of 23 ft or more; kinds by hookups: full (water, sewer, electric), water and electric,
electric only, none. Senior discounts (the parks' camping policy): Arkansas residents 62+ pay half Sunday-Thursday and
25% less on weekends and holidays; out-of-state 62+ 25% less Sunday-Thursday."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
cal = json.load(open(os.path.join(HERE, "ar_calendar_2026-10-12.json"), encoding="utf-8"))["parks"]
WORD = {"fhu": "full-hookup sites", "ew": "water-and-electric sites", "e": "electric-only sites", "n": "sites without hookups"}
SHARED = (5153, 5154)        # Mississippi River SP: one calendar, sites named 'Campsite N' for Beech Point and Storm Creek Lake


def kind(r):
    el = (r.get("amps") or "").strip() not in ("", "None", "0")        # 'None' is a string on primitive sites
    if el and r.get("sewer") == "true":
        return "fhu"
    if el and r.get("water") == "true":
        return "ew"
    return "e" if el else "n"


out, flags = [], []
for eid, e in sorted(rows.items()):
    if e.get("kind") != "campground" or e.get("state") != "AR" or e.get("ownership") != "state" or e.get("fees"):
        continue
    m = re.search(r"reserve\.arkansasstateparks\.com/([a-z0-9-]+)", e.get("website") or "")
    slug = m.group(1) if m else ("village-creek" if eid == 5129 else None)
    slug = {"davidsonville-historic": "davidsonville"}.get(slug, slug)     # the entry's link uses a slug that no longer resolves
    if not slug or slug not in cal:
        flags.append((eid, e["name"], "no calendar")); continue
    rvrows = [(maxrv, kind({"amps": amps, "water": water, "sewer": sewer}), nights)
              for data in cal[slug].values() for site, usetype, maxrv, water, sewer, amps, access, nights in data.get("rows", [])
              if "rv" in (usetype or "")]
    # A blank max length counts only for a kind with no recorded length at the park (all of Queen Wilhelmina's and Moro
    # Bay's sites); Lake Ouachita's blank primitive sites sit beside identical ones recorded at 16 ft.
    measured = {k for maxrv, k, _ in rvrows if (maxrv or "").isdigit()}
    prices, nolen = collections.defaultdict(list), 0
    for maxrv, k, nights in rvrows:
        if (maxrv or "").isdigit():
            if int(maxrv) < 23:
                continue
        elif k in measured:
            continue
        else:
            nolen += 1
        prices[k] += [p for p in nights if p is not None]
    prices = {k: v for k, v in prices.items() if v}       # a kind whose every night was booked has no price
    if not prices:
        flags.append((eid, e["name"], f"no bookable RV night in either window ({slug})")); continue
    order = sorted(prices, key=lambda k: min(prices[k]))
    base = order[0]
    lo, hi = min(prices[base]), max(prices[base])
    parts = [(f"${min(prices[k]):.2f}-{max(prices[k]):.2f}" if min(prices[k]) != max(prices[k]) else f"${min(prices[k]):.2f}")
             + f" for {WORD[k]}" for k in order]
    note = parts[0] + ("; " + "; ".join(parts[1:]) if len(parts) > 1 else "") + \
        (". The price changes by site and night (demand and season), plus tax and a reservation fee. Arkansas residents "
         "62+ pay half Sunday-Thursday and 25% less on weekends; out-of-state 62+ 25% less Sunday-Thursday. Every "
         f"bookable night on the park's calendar for two weeks from 2026-10-13 and from 2027-06-15, read {D}." +
         (" The calendar lists Beech Point's and Storm Creek Lake's sites together, so both entries carry the park's range."
          if eid in SHARED else "") + (" The calendar gives no maximum RV length for these sites." if nolen else ""))
    fees = {"nightly_low": round(lo, 2), "nightly_high": round(hi, 2), "currency": "USD", "checked": "2026", "note": note}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"https://reserve.arkansasstateparks.com/{slug}/camping (Calendar View, every RV site's nightly rate for "
                          f"two weeks from 2026-10-13 and from 2027-06-15; 'The quoted rate for each night does not include taxes or "
                          f"the reservation fee'), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "AR findings;", len(flags), "flagged")
for x in out:
    print(x["id"], x["name"][:36], x["fees"]["nightly_low"], x["fees"]["nightly_high"], "|", x["fees"]["note"][:150])
for f in flags:
    print("FLAG", *f)
