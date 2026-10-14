# roverpass_api.py OUT.jsonl ID:SLUG [ID:SLUG ...]
# roverpass_api.py OUT.jsonl --slugs SLUGS.json [--only ID,ID,...]
# RoverPass prices read from RoverPass's own booking API (2026-10-14, written to price the tier-only entries that link
# to RoverPass). Plain HTTP, no browser: a GET of the park's /c/<slug>/booking/ page gives the session cookie, the
# csrf-token meta and the static API token (the data-token attribute of #react-data-container), and every query is a
# GraphQL POST to /api/queries/ carrying 'Authorization: Bearer <token>', 'x-csrf-token' and 'apollo-require-preflight'.
# Introspection is off; the queries below are the booking app's own (packs/js/checkout-*.js), trimmed:
#  - campground(slug): the park record. isBookable is the line between a park that takes bookings through RoverPass and
#    a directory listing nobody has claimed (its page shows "Claim my Campground" and "Last Updated: 11/15/2024", and
#    its rate table is not the operator's: .claude/memory/feedback_note_rate_sourcing.md). isRequest marks request-to-
#    book parks (the operator confirms each booking); systemType 'CRS' is RoverPass's own reservation system with site
#    inventory. closeSeasonDates are the park's closures, each {from, to}, both days closed. A listing that isn't
#    bookable answers null for several non-null fields (advancedMonths ...), which fails the whole query, so those
#    are asked separately (MORE), and only of a bookable park.
#  - campground(slug, from, to, filters): availability {isAvailable, message} ("Campground is closed"), every rate on
#    sale for those nights (ratesAvailableDuring) with its type ('siteTypeName' = "<type label> - <rate name>"), night
#    price for those dates, longest rig (maxLength, a list; "0" = none set), amenities and minimum nights, and the
#    rates that need a longer stay (unavailableRatesMinNightsList). A closed date lists no rates at all (unlike
#    Campspot, which prices closed dates).
#  - sitesAvailableDuring(rateId): that rate's open sites, each with its longest rig.
#  - purchasePricing(reservationsData): the cart - the site charge, any fee of the park's own (items with isFee), and
#    RoverPass's platform fee, the processing fee and tax, which are the platform's and the state's and never stored.
#
# Per park: the record; then, when it is bookable, one night from each date in DATES (a Tuesday and a Saturday in
# October 2026, January 2027 and June 2027 - the Campspot pass's dates, none a holiday weekend). If none of them opens
# an RV rate, the first Tuesday and Saturday after the park's current closure, or else from the day after tomorrow
# (rec["fallback"]). Then each RV rate's open sites on its first open date, and a cart for one and for two nights, 2
# adults, on the cheapest and the dearest RV rate a 23-ft rig fits, from its first open date: the quotes that tell a
# per-stay fee from a per-night one. One JSON line per park; roverpass_tier_build.py reads them.
#
# PACE: one call per RP_PAUSE seconds (default 1). A failed call is retried once on a fresh session after 10 s; a
# second failure stops the run without writing the park being read, so the same command resumes (parks already in
# OUT are skipped).
import datetime, http.cookiejar, json, os, re, sys, time, urllib.error, urllib.request

PAUSE = float(os.environ.get("RP_PAUSE", "1"))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
API = "https://www.roverpass.com/api/queries/"
DATES = ["2026-10-20", "2026-10-17", "2027-01-26", "2027-01-30", "2027-06-08", "2027-06-12"]
# the site types an RV may be sold under (RoverPass's own labels, 'options.siteTypes'); the rest are cabins, tents,
# storage, stalls, rentals ('RVs in Place' are the park's own RVs) and the like
RVISH = ("RV Sites", "Overnight Camping", "Overnight Parking", "Caravan Sites", "Misc")
# not a nightly RV site, by name: the Campspot pass's list (campspot_tier_build.py) - keep the two in step
SKIP = (r"(?i)\bgroup\b|horse|equestrian|\brally\b|^(?!.*\b(rv|camper|trailer)\b).*\btent\b|cabin|lodge|bunkhouse|"
        r"double site|buddy|pavilion|day use|day pass|^(?!.*\b(rv|camper|trailer)\b).*\b(boat slip|dock|slip)\b|"
        r"storage|glamp|yurt|tipi|teepee|cottage|motel|\broom\b|accessible|\bada\b|handicap|"
        r"^(?!.*\b(daily|nightly|night|overnight|transient)\b).*(season|monthly|long[- ]term|\bweekly\b|annual|"
        r"yearly|winter stay)")
INFO = ("id slug name fullAddress cityName stateName phone email isBookable isRequest isInventory isAutoAssign "
        "systemType closeSeasonDates canUseAccommodationNightly canUseAccommodationDaily measureUnit currency { code }")
MORE = ["advancedMonths", "campgroundCancellationPolicy", "cancellationPolicyConfig { fullDays halfDays name }",
        "checkInProcedure", "rulesList", "whatToKnow", "nonRefundableDiscount", "canChooseSite"]
RC = ("fragment RC on Rate { id name siteTypeName amenities accessibility description maxLength maxWidth "
      "minNightsRequired inPersonBookingOnly inPersonBookingMessage rigRequired totalNights "
      "nightPrice { amount display } totalPrice { amount display } }")
DAY = ("query D($slug: String!, $from: ISO8601Date!, $to: ISO8601Date!, $filters: ValidationsFiltersAttributes) { "
       "campground(slug: $slug, from: $from, to: $to, filters: $filters) { id alerts availability { isAvailable message } "
       "ratesAvailableDuring { ...RC } unavailableRatesMinNightsList { ...RC } sitesCountByTypeDuring "
       "siteTypesNeedingLongerStay unavailableDueToHolidays unavailableSitesTypesCount } } " + RC)
SITES = ("query S($slug: String!, $from: ISO8601Date!, $to: ISO8601Date!, $rateId: ID!) { campground(slug: $slug, "
         "from: $from, to: $to) { id sitesAvailableDuring(rateId: $rateId) { id name description amenities maxLength "
         "maxWidth maxPeople } } }")
PRICING = ("query P($reservationsData: [ReservationPricingAttributes!], $slug: String!, $tickets: [TicketAttributes!]) "
           "{ campground(isPos: false, slug: $slug) { id purchasePricing(reservationsData: $reservationsData, "
           "tickets: $tickets) { isTaxIncluded lineItems { description price { amount } quantity subtotal { amount } } "
           "platformFeeTotal { display } processingFeeTotal { amount display } reservations { from to "
           "pricing { subtotal { amount display } items { name isFee base { amount display } units priceDescription "
           "itemableType } } rate { id name } site { id name } } subtotal { amount display } taxName "
           "taxTotal { amount display } total { amount display } } } }")


class Blocked(Exception):
    pass


S = {}


def session(slug):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    page = f"https://www.roverpass.com/c/{slug}/booking/"
    h = op.open(urllib.request.Request(page, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")
    S.update(op=op, page=page, csrf=re.search(r'name="csrf-token" content="([^"]+)"', h).group(1),
             tok=re.search(r"data-token=['\"]([^'\"]+)['\"]", h).group(1))


def post(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    for attempt in (1, 2):
        time.sleep(PAUSE)
        try:
            if not S:
                session("back-40-campground-rushylvania-oh")
            hd = {"User-Agent": UA, "Content-Type": "application/json", "Accept": "*/*",
                  "apollo-require-preflight": "true", "x-csrf-token": S["csrf"], "Origin": "https://www.roverpass.com",
                  "Referer": S["page"], "Authorization": "Bearer " + S["tok"]}
            r = S["op"].open(urllib.request.Request(API, data=body, headers=hd), timeout=60)
            return json.loads(r.read().decode())
        except (urllib.error.URLError, OSError, ValueError, AttributeError) as ex:
            print("  call failed:", str(ex)[:120], flush=True)
            if attempt == 2:
                raise Blocked(str(ex)[:200])
            time.sleep(10)
            S.clear()


def info(slug):
    """The park record: INFO, then for a bookable park whichever MORE fields it answers (a null in one fails the
    query, and a listing that isn't bookable answers null to most of them, so it is not asked)."""
    r = post("query C($slug: String!) { campground(slug: $slug) { %s } }" % INFO, {"slug": slug})
    g = (r.get("data") or {}).get("campground")
    if not g or not g.get("isBookable"):
        return g, r.get("errors")
    more = list(MORE)
    while True:
        r = post("query C($slug: String!) { campground(slug: $slug) { %s %s } }" % (INFO, " ".join(more)),
                 {"slug": slug})
        bad = {e["path"][-1] for e in r.get("errors") or [] if e.get("path")}
        if not bad or not more:
            return (r.get("data") or {}).get("campground"), r.get("errors")
        more = [m for m in more if m.split(" ")[0] not in bad]


def next_day(d, n=1):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(n)).isoformat()


def rv_rate(rt):
    return (rt.get("siteTypeName") or "").split(" - ")[0] in RVISH and not re.search(SKIP, rt.get("name") or "")


def fits(rt):
    ls = [int(x) for x in rt.get("maxLength") or [] if str(x).isdigit()]
    return not ls or 0 in ls or max(ls) >= 23


def read(eid, slug):
    today = datetime.date.today()
    rec = {"id": eid, "slug": slug, "read": today.isoformat()}
    g, errs = info(slug)
    rec["info"] = g
    if errs:
        rec["info_errors"] = [e.get("message") for e in errs][:4]
    if not g:
        rec["error"] = "no campground for that slug"
        return rec
    if not g.get("isBookable"):
        return rec
    days = {}

    def day(d):
        r = post(DAY, {"slug": slug, "from": d, "to": next_day(d), "filters": {"dayUse": False}})
        days[d] = (r.get("data") or {}).get("campground") or {"errors": r.get("errors")}
    for d in DATES:
        day(d)
    is_open = lambda d: any(rv_rate(rt) for rt in days[d].get("ratesAvailableDuring") or [])
    if not any(map(is_open, days)):
        cands = []
        for c in g.get("closeSeasonDates") or []:
            if c["to"] >= today.isoformat() and c["from"] <= (today + datetime.timedelta(400)).isoformat():
                start = datetime.date.fromisoformat(c["to"]) + datetime.timedelta(1)
                break
        else:
            start = today + datetime.timedelta(2)
        tue = start + datetime.timedelta((1 - start.weekday()) % 7)
        sat = start + datetime.timedelta((5 - start.weekday()) % 7)
        rec["fallback"] = [x.isoformat() for x in (tue, sat) if x.isoformat() not in days]
        for d in rec["fallback"]:
            day(d)
    rec["dates"] = days
    # each RV rate's open sites, on its first open date
    first = {}
    for d in sorted(days):
        for rt in days[d].get("ratesAvailableDuring") or []:
            if rv_rate(rt) and rt["id"] not in first:
                first[rt["id"]] = (d, rt)
    rec["sites"] = {}
    for rid, (d, rt) in first.items():
        r = post(SITES, {"slug": slug, "from": d, "to": next_day(d), "rateId": rid})
        rec["sites"][rid] = {"date": d, "sites": ((r.get("data") or {}).get("campground") or {}).get(
            "sitesAvailableDuring"), "errors": r.get("errors")}
    # carts on the cheapest and the dearest fitting RV rate, one and two nights from its first open date (a Tuesday
    # where there is one)
    fit = [(d, rt) for rid, (d, rt) in first.items() if fits(rt) and (rt.get("nightPrice") or {}).get("amount")]
    pick = []
    if fit:
        price = lambda x: x[1]["nightPrice"]["amount"]
        pick = [min(fit, key=price)]
        if price(max(fit, key=price)) != price(pick[0]):
            pick.append(max(fit, key=price))
    rec["pricing"] = []
    for d, rt in pick:
        tues = [x for x in sorted(days) if datetime.date.fromisoformat(x).weekday() == 1 and any(
            y["id"] == rt["id"] for y in days[x].get("ratesAvailableDuring") or [])]
        d = tues[0] if tues else d
        for n in (1, 2):
            res = [{"extras": {"filters": {"maxLength": None, "maxWidth": None},
                               "guests": {"adults": 2, "children": 0, "pets": 0, "petBreeds": "", "vehicles": 0,
                                          "vehiclesTowed": False},
                               "isSiteLock": False, "marketplace": True, "productsPurchased": []},
                    "from": d, "inProgress": True, "rateId": rt["id"], "to": next_day(d, n)}]
            r = post(PRICING, {"reservationsData": res, "slug": slug, "tickets": []})
            rec["pricing"].append({"rate": rt["id"], "name": rt["name"], "from": d, "nights": n,
                                   "resp": ((r.get("data") or {}).get("campground") or {}).get("purchasePricing"),
                                   "errors": r.get("errors")})
    return rec


def main():
    out = sys.argv[1]
    args = sys.argv[2:]
    if "--slugs" in args:
        sl = json.load(open(args[args.index("--slugs") + 1], encoding="utf-8"))
        only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else None
        todo = [(int(k), v["slug"]) for k, v in sl.items() if only is None or k in only]
    else:
        todo = [(int(a.split(":", 1)[0]), a.split(":", 1)[1]) for a in args]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["id"] for l in open(out, encoding="utf-8") if l.strip()}
    n = 0
    with open(out, "a", encoding="utf-8") as fh:
        for eid, slug in todo:
            if eid in done:
                continue
            try:
                rec = read(eid, slug)
            except Blocked as ex:
                print(f"STOPPED at {eid} {slug}: {ex}; run the same command again to resume", flush=True)
                break
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            n += 1
            g = rec.get("info") or {}
            opened = [d for d, v in (rec.get("dates") or {}).items()
                      if any(rv_rate(rt) for rt in v.get("ratesAvailableDuring") or [])]
            print(eid, slug, "bookable" if g.get("isBookable") else ("NOT bookable" if g else rec.get("error")),
                  "| open", opened, "| carts", len(rec.get("pricing") or []), flush=True)
    print(n, "parks written")


if __name__ == "__main__":
    main()
