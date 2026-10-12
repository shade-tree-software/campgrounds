#!/usr/bin/env python3
"""Nightly campsite fees off a GoingToCamp (Camis) reservation site (2026-10-10).

    python3 audit/price_research/gtc_prices.py --host wisconsin.goingtocamp.com \
        --entries ENTRIES.json OUT.json [--dates 2027-05-11,2027-06-15]

GoingToCamp shows a site's price only after you pick the site, but the panel
gets it from a plain call: POST /api/resource/feeDetails?resourceId=..&startDate=..
(body: the booking's capacity counts, [] for none) answers
{"resourceFeeDetails": [{"feeTotal": 40.0, ...}]} - one night's fee for that site.
Sites sharing a feeScheduleId share a fee, so one call per schedule per date.

ENTRIES.json: [{"id", "park", "campground"}] - `park` is matched against the
resource location names, `campground` (optional) against the park's map titles;
every site under that map subtree counts. Only Campsite-category sites whose
allowed equipment includes a trailer/RV class that fits a 23-ft rig ("up to
25'" or longer) are priced, so walk-in tent sites can't set nightly_low.
Writes findings for apply.py; prints what it matched so a wrong map is visible.
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request, http.cookiejar

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
CAMPSITE = "Campsite"


def is_campsite(name):
    """'Campsite', or a named variant of it ('Campsite/Monthly Campsite', 'Gulf View Campsite' on
    reserve.mdwfp.com, 2026-10-12); primitive, group and tent categories are not RV sites."""
    name = name or ""
    return name == CAMPSITE or (CAMPSITE.lower() in name.lower()
                                and not re.search(r"(?i)primitive|group|tent|walk|boat", name))


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower().replace("'", "")).strip()


class GTC:
    def __init__(self, host):
        self.base = f"https://{host}"
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.op.addheaders = [("User-Agent", UA), ("Accept", "application/json, text/plain, */*")]
        self.op.open(self.base + "/", timeout=30).read()

    def get(self, ep):
        time.sleep(0.3)
        return json.load(self.op.open(self.base + ep, timeout=40))

    def fee(self, resource_id, date):
        q = urllib.parse.urlencode({"resourceId": resource_id, "startDate": date, "boatLength": 0,
                                    "bookingCategoryId": 0, "entryPointResourceId": 0, "exitPointResourceId": 0})
        req = urllib.request.Request(f"{self.base}/api/resource/feeDetails?{q}", data=b"[]", method="POST",
                                     headers={"Content-Type": "application/json"})
        time.sleep(0.4)
        d = json.load(self.op.open(req, timeout=40))
        fees = [f.get("feeTotal") for f in d.get("resourceFeeDetails") or [] if f.get("feeTotal") is not None]
        return sum(fees) if fees else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--entries", required=True)
    ap.add_argument("--dates", default="2027-05-11,2027-06-15")
    ap.add_argument("--currency", default="USD", choices=["USD", "CAD"])
    ap.add_argument("--max-fee", type=float, default=None,
                    help="drop fees above this: a 'Campsite/Monthly Campsite' site can answer with its monthly rate")
    ap.add_argument("out")
    a = ap.parse_args()
    dates = a.dates.split(",")
    g = GTC(a.host)
    locs = {(r["localizedValues"][0].get("fullName") or ""): r["resourceLocationId"] for r in g.get("/api/resourceLocation")}
    cats = {c["resourceCategoryId"]: c["localizedValues"][0]["name"] for c in g.get("/api/resourcecategory")}
    subs = {}
    for c in g.get("/api/equipment"):
        for s in c.get("subEquipmentCategories", []):
            subs[s["subEquipmentCategoryId"]] = s["localizedValues"][0]["name"]
    # a sub-category fits a 23-ft rig when it is a trailer/RV class whose limit is >= 25 ft
    fits = {sid for sid, name in subs.items()
            if re.search(r"(?i)trailer|rv", name) and (re.search(r"(?i)over", name) or
                                                         int((re.search(r"(\d+)", name) or [0, "0"])[1]) >= 25)}
    cache, out = {}, []
    for e in json.load(open(a.entries)):
        park = [n for n in locs if norm(e["park"]) == norm(n)] or [n for n in locs if norm(e["park"]) in norm(n)]
        if not park:
            print(e["id"], "NO PARK", e["park"]); continue
        lid = locs[park[0]]
        if lid not in cache:
            maps = g.get(f"/api/maps?resourceLocationId={lid}")
            res = g.get(f"/api/resourcelocation/resources?resourceLocationId={lid}")
            cache[lid] = (maps, res)
        maps, res = cache[lid]
        by_id = {m["mapId"]: m for m in maps}

        def subtree(mid, seen=None):
            seen = seen or set()
            if mid in seen or mid not in by_id:
                return set()
            seen.add(mid)
            m = by_id[mid]
            ids = {r["resourceId"] for r in m.get("mapResources") or []}
            for l in m.get("mapLinks") or []:
                ids |= subtree(l.get("childMapId"), seen)
            return ids

        if e.get("campground"):
            want = norm(e["campground"])
            hit = [m for m in maps if norm(m["localizedValues"][0]["title"]) == want] or \
                  [m for m in maps if want in norm(m["localizedValues"][0]["title"])]
            if not hit:
                print(e["id"], "NO MAP", e["campground"], "in", [m["localizedValues"][0]["title"] for m in maps]); continue
            rids = set().union(*(subtree(m["mapId"]) for m in hit))
            label = " + ".join(m["localizedValues"][0]["title"] for m in hit)
        else:
            rids = {int(k) for k in res}
            label = "(whole park)"
        sites = [r for k, r in res.items() if int(k) in rids and is_campsite(cats.get(r.get("resourceCategoryId")))
                 and any(x.get("subEquipmentCategoryId") in fits for x in r.get("allowedEquipment") or [])]
        groups = {}
        for r in sites:
            groups.setdefault(r.get("feeScheduleId"), r)
        fees = {}
        for fs, r in groups.items():
            for d in dates:
                v = g.fee(r["resourceId"], d)
                if v is not None:
                    fees.setdefault(fs, []).append((d, v, r["localizedValues"][0]["name"]))
        vals = [v for lst in fees.values() for _, v, _ in lst if a.max_fee is None or v <= a.max_fee]
        print(e["id"], park[0], "|", label, "|", len(sites), "RV sites,", len(groups), "fee schedules |",
              sorted(set(vals)) if vals else "no fee")
        if not vals:
            continue
        lo, hi = min(vals), max(vals)
        lo, hi = (int(v) if float(v).is_integer() else round(v, 2) for v in (lo, hi))
        out.append({"id": e["id"], "fees": {"nightly_low": lo, "nightly_high": hi, "currency": a.currency,
                    "note": f"Base nightly fee (before any nonresident surcharge) for RV-capable sites ({len(sites)} sites, {len(groups)} fee "
                            f"schedules), Tuesday nights {' and '.join(dates)}, from the {a.host} site fee panel."},
                    "source": f"https://{a.host}/api/resource/feeDetails ({park[0]} / {label}; "
                              f"read {__import__('datetime').date.today().isoformat()})"})
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(len(out), "findings ->", a.out)


if __name__ == "__main__":
    main()
