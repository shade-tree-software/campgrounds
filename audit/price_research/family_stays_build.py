"""Nightly rates for the private and local campgrounds the family has stayed at (AWH 2026-10-13: "start on the private
and local campgrounds the family has stayed at"), read 2026-10-13.

    python3 -I family_stays_build.py OUT.json        # then: python3 apply.py OUT.json [--apply]

The 25 visited campgrounds with no dollar figure (18 private, 7 local); 24 are priced here, and Gary's 130 stays
unpriced on AWH's 2026-10-11 call. Page texts are in family_stays_pages_2026-10-13.txt; the Campspot quotes in family_stays_campspot_2026-10-13.jsonl.

Shape, as in the other private and local entries priced since 2026-10-11: nightly_low / nightly_high run from the
cheapest to the dearest regular (non-holiday) night of an RV site a 23-ft rig fits, at two adults, before tax, across
the site types and the posted seasons; a per-reservation charge is reservation_fee; the note gives the grid.

Campspot (audit/private_gap_browser/campspot_batch.py, kept as family_stays_campspot_2026-10-13.jsonl): each park's RV
site types a 23-ft rig fits, then campspot_site.py's price breakdown of every one of them for one night from a Tuesday
and from a Saturday ('$52.92 x 1 night', 'Campground Fees $6.00', 'Site Total') - June 2027 where the park has it
loaded and bookable, otherwise the nearest dates that are. The availability API's per-night figure is the Site Total
less tax, so it folds the park's own fee and Campspot's booking fee into the rate; here the site rate and the fee are
recorded apart, and a flat
'Campground Fees' line is reservation_fee only after a 2-night quote showed it once per stay (the 'two_night'
records). Campspot's own 'Booking Fee' (3%, at least $3) is the platform's, not the park's, and goes in the note
only, as Hipcamp's service fee does. Campspot carries a remembered pet count into any search whose URL leaves pets
out, so every quote was taken for 2 adults and nothing else."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = "2026-10-13"
CS = os.path.join(HERE, "family_stays_campspot_2026-10-13.jsonl")
TUE, SAT = "2027-06-15", "2027-06-19"


def num(v):
    return int(v) if float(v).is_integer() else round(v, 2)


def cash(v):
    return f"${num(v)}" if float(v).is_integer() else f"${v:.2f}"


# ---- Campspot parks. dates: the Tuesday and Saturday quoted. fee: the park's flat 'Campground Fees', shown once per stay
# by a two_night record. skip: site types left out (named in extra).
CAMPSPOT = {
    663: dict(slug="bearruncampground", dates=(TUE, SAT), fee=6,
              extra="The park's rules: a reservation that asks for a particular site takes 2 nights on a weekend and 3 "
                    "on a holiday.",
              also="https://bearruncampground.com/our-campground/map-and-rules/ ('Any specific site requested requires the "
                   "following minimum reservations: Weekends: 2 nights, Holidays: 3 nights.')"),
    572: dict(slug="northpointervresort", dates=("2027-03-16", "2027-03-20"),
              extra="June 2027 showed the same prices but is past the park's 180-day booking window."),
    665: dict(slug="mountaintoprvcampground", dates=(TUE, SAT), fee=5),
    661: dict(slug="wheelincampground", dates=(TUE, SAT), fee=5),
    805: dict(slug="palmettoshoresrvresort", dates=(TUE, SAT), fee=5, skip=r"^Buddy Site$",
              extra="A Buddy Site is two neighbouring sites booked together ($165, $175 on the Saturday), left out."),
    540: dict(slug="wcrc", dates=(TUE, SAT), fee=3),
    754: dict(slug="deepbendlanding", dates=("2026-10-20", "2026-10-24"),
              extra="Campspot has no 2027 dates yet. The park's own price list (no year) has the Deluxe at $55 and the "
                    "others as here; there is no bathhouse, so units must be self-contained.",
              also="https://www.deepbendlanding.com/ ('RV SITE PRICES')"),
    561: dict(slug="stow-silversprings", dates=("2026-10-20", "2026-10-24"),
              extra="The city adds 3% of the site charge ('Campground Fees', $0.66 a night). Its page: 2026 season April "
                    "10 - October 31 at $22.00 per night; electric hookups, water from spigots (no water hookup), a dump "
                    "station; cancelling costs $5. Campspot has no 2027 dates yet.",
              also="https://www.stowohio.gov/338/Stow-Silver-Springs-Campground ('Site Fees: $22.00 per night')"),
    578: dict(slug="munisingtouristparkcampground", dates=("2026-10-14", "2026-10-17"),
              extra="Reservations run May 14 - October 17 (leaving October 18), so those are the season's last nights; "
                    "2027 opens for booking December 1 and isn't loaded yet, so summer prices could not be checked. The "
                    "park's page says 'RV Camping Starting at $55' (20/30/50-amp, water and sewer) and 'RV-Lite starting "
                    "at $45' (back-in sites in the trees, some with 30/20-amp and water); at most 14 days.",
              also="https://munisingtouristpark.com/ ('RV Camping Starting at $55', 'RV-Lite starting at $45', the "
                   "reservation dates)"),
}


def day(d):
    import datetime
    return datetime.date.fromisoformat(d).strftime("%A")


def parse_lines(lines):
    """campspot_site.py lines -> [(type name, nightly site rate, nights, {fee line: amount})]."""
    out = []
    for x in lines:
        m = re.match(r"^\d+ (.*?): \$([\d,.]+) x (\d+) nights? \| \$[\d,.]+ \| (.*)$", x)
        if m:
            parts = m.group(4).split(" | ")
            extras = {parts[i]: float(parts[i + 1].lstrip("$").replace(",", "")) for i in range(0, len(parts) - 1, 2)}
            out.append((m.group(1), float(m.group(2).replace(",", "")), int(m.group(3)), extras))
    return out


def campspot_findings():
    recs, two = {}, collections.defaultdict(list)
    for line in open(CS, encoding="utf-8"):
        r = json.loads(line)
        if "two_night" in r:
            two[r["id"]] += parse_lines(r["two_night"])
        else:
            recs[(r["id"], tuple(r.get("dates") or (TUE, SAT)))] = r      # the last record for those dates wins
    out = []
    for eid, spec in CAMPSPOT.items():
        d1, d2 = spec["dates"]
        r = recs[(eid, (d1, d2))]
        rates = collections.defaultdict(dict)      # type name -> {date: rate}
        fees, booking = set(), False
        for d in (d1, d2):
            for name, rate, nights, extras in parse_lines(r["breakdown"][d]):
                assert nights == 1, (eid, d, name)
                if spec.get("skip") and re.search(spec["skip"], name):
                    continue
                rates[name][d] = rate
                fees.add(extras.get("Campground Fees", 0.0))
                booking |= "Booking Fee" in extras
        fee = spec.get("fee")
        if fee:
            assert fees == {fee}, (eid, fees)
            longer = [e for e in two[eid] if e[2] >= 2]
            assert longer and all(e[3].get("Campground Fees") == fee for e in longer), (eid, "fee not shown per stay")
        else:
            assert not (fees - {0.0}) or eid == 561, (eid, fees)
        groups = collections.defaultdict(list)      # (Tuesday rate, Saturday rate) -> type names
        for name, by in rates.items():
            groups[(by[d1], by.get(d2))].append(name)
        parts = []
        for (a, b), names in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
            names = sorted(names)
            label = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
            parts.append(f"{label} {cash(a)}" + (f" ({cash(b)} on the {day(d2)})" if b is not None and b != a else ""))
        allv = [v for by in rates.values() for v in by.values()]
        text = (f"Campspot, one night for 2 adults from a {day(d1)} ({d1}) and from a {day(d2)} ({d2}), site rate before "
                f"tax: " + "; ".join(parts) + "."
                + (f" Plus the park's {cash(fee)} campground fee, once per stay." if fee else "")
                + (f" {spec['extra']}" if spec.get("extra") else "")
                + (" Campspot adds its own booking fee at checkout (3%, at least $3)." if booking else "")
                + f" Read {D}.")
        fees_obj = {"nightly_low": num(min(allv)), "nightly_high": num(max(allv)), "currency": "USD"}
        if fee:
            fees_obj["reservation_fee"] = num(fee)
        fees_obj.update(checked="2026", note=text)
        out.append({"id": eid, "fees": fees_obj,
                    "source": f"https://www.campspot.com/book/{spec['slug']} (each RV site type's price breakdown for one "
                              f"night from {d1} and from {d2}, 2 adults"
                              + ("; a 2-night quote for the per-stay fee" if fee else "")
                              + "; family_stays_campspot_2026-10-13.jsonl)"
                              + (f" + {spec['also']}" if spec.get("also") else "") + f", read {D}"})
    return out


# ---- Posted rates, typed from family_stays_pages_2026-10-13.txt
HAND = [
    {"id": 660, "fees": {
        "nightly_low": 38, "nightly_high": 66, "currency": "USD", "checked": "2026",
        "note": ("Port of Erie's 2027 rates, one rate for every site: Sunday-Thursday $51 in May and September, $56 in "
                 "June-August, $38 in October; Friday-Saturday $57, $66 and $46; holidays $67 and $73. The 2026 rates "
                 "were $47 / $50 / $34 and $53 / $58 / $40. Rates are for one family and one RV per site. Season May 1 - "
                 "October 31; paid in full when booked. Read " + D + ".")},
     "source": "https://www.porterie.org/wp-content/uploads/2026/03/2026-2027-campground-rate-sheet-FINAL.pdf ('Lampe "
               "Campground Rates 2026/2027', linked from https://www.porterie.org/lampecampground/ as 'current rates'), "
               "read " + D},
    {"id": 1190, "fees": {
        "nightly_low": 35, "nightly_high": 37, "currency": "USD", "reservation_fee": 3.5, "checked": "2026",
        "note": ("RV sites (30-amp electric, 50-amp at nine of the 28; no water hookup at the site) $35 a night Sunday-"
                 "Thursday, $37 Friday, Saturday and holidays; 'A $3.50 processing fee is charged for all reservations.' "
                 "Campers' guests need a day pass ($5) and must leave by 9 PM. The rec area's pages give no year for the "
                 "rates. Read " + D + ".")},
     "source": "https://www.quefamilyrec.com/ ('Park Fees': RV Campsites Weekday $35, Weekend $37; processing fee) + "
               "https://www.quefamilyrec.com/camping ('RV Site Fees'), read " + D},
    {"id": 644, "fees": {
        "nightly_low": 45.5, "nightly_high": 47.5, "currency": "USD", "checked": "2026",
        "note": ("Pinellas County's year-round rates for sites 86-236, which take every camping unit: $45.50 a night, "
                 "$47.50 on the water, plus 6% tourist development tax and 7% state tax ($51.42 / $53.68). Sites 1-85 "
                 "($40.50 / $42.50) are for tents, vans, pop-ups and trailers under 16 ft. Every site has water and "
                 "30/50-amp electric. At most 14 nights in any 30 days; booking opens six months ahead (seven for county "
                 "residents); each change or cancellation costs either a $10 administrative fee or a penalty equal to the "
                 "site's cost. Read " + D + ".")},
     "source": "https://pinellas.gov/park/camping.htm ('Year-Round Rates Plus Tax Per Night': Sites 86-236 Non-waterfront "
               "$45.50, Waterfront $47.50), read " + D},
    {"id": 12, "fees": {
        "nightly_low": 35, "nightly_high": 60, "currency": "USD", "reservation_fee": 5, "checked": "2026",
        "note": ("2026 fees per site: sites with no hookups (the page calls them 'PRIMITIVE (TENT)') $35 away from the "
                 "river and $45 on it, Sunday-Thursday, $40 / $50 on weekends and holidays; riverfront electric sites $55, "
                 "$60 on weekends and holidays; the electric fees include two people and two vehicles, each extra person $12 "
                 "a night, an extra vehicle pass $5. The deposit is the first night at the weekday rate plus a $5 "
                 "reservation fee per site; it isn't refunded but can move to another date with 10 days' notice. "
                 "Read " + D + ".")},
     "source": "https://lowwaterbridgecampground.com/camping-at-lwbc ('2026 Camping Fees'), read " + D},
    {"id": 10, "fees": {
        "nightly_low": 60, "nightly_high": 60, "currency": "USD", "checked": "2026",
        "note": ("Daily site rates by row, chosen by RV length: A row (0-32 ft) $60, B row (26-36 ft) $60, C row (37-100 "
                 "ft) $80, D row (37-100 ft) $100. Every site has water and 30/50-amp electric and none has sewer (free "
                 "dump station; honey-truck pump-out $30). Monthly $1,200, premium $1,300. The page gives no year. "
                 "Read " + D + ".")},
     "source": "https://watermelonpark.com/ ('Daily Site Rates'), read " + D},
    {"id": 662, "fees": {
        "nightly_low": 68, "nightly_high": 68, "currency": "USD", "checked": "2026",
        "note": ("2027 full-hookup base site rate $68 a night ('subject to change due to availability'; $61 in 2026) for "
                 "up to 4 people; overnight guests beyond them $9 each a night; choosing your site (lock site) $10 more; "
                 "stay six nights and get one free. Monthly $700 in 2027. Booking on Staylist. Read " + D + ".")},
     "source": "https://silvercanoecampground.com/rates--cancelation-policy.html ('2027 NIGHTLY RATE: ... Full Hook-Up Base "
               "Site Rate $68.00'), read " + D},
    {"id": 553, "fees": {
        "nightly_low": 65, "nightly_high": 105, "currency": "USD", "checked": "2026",
        "note": ("Summer 2025 daily rates (May 1 - October 31, 2025), the latest the park posts: Choice $65, Prime $68, "
                 "Select $80, Superior $94, Ultimate $105, for 2 people ($5 a day each extra person); holidays (Memorial "
                 "Day, the Fourth of July, Labor Day) a 3-night minimum and $5 a night more. Winter: January-March by "
                 "the month only; November and April show only monthly prices ($1,085-1,630 plus electric for 2025-26), "
                 "and no winter daily rate is posted. No online booking: the park asks for requests through its contact page. "
                 "Read " + D + ".")},
     "source": "https://www.sancarlosrv.com/copy-of-home (the park's 'Rates' page: 'Summer Seasonal Rates MAY 1st 2025 "
               "through OCTOBER 31, 2025', daily Choice $65.00 ... Ultimate $105.00) + https://www.sancarlosrv.com/ ('We "
               "don't accept online reservations'), read " + D},
    {"id": 757, "fees": {
        "nightly_low": 40.5, "nightly_high": 40.5, "currency": "USD", "checked": "2026",
        "note": ("Hipcamp listing: three RV sites (Farm View 2 and 3, Blue View 1; electric and water hookups, rigs to 60-70 "
                 "ft) at $40.50 a night before Hipcamp's service fee ($7.42 a night shown); one-night stays allowed. The "
                 "riverside canoe sites are listed for tents only ($42.75). Read " + D + ".")},
     "source": "https://www.hipcamp.com/en-US/land/south-carolina-black-pearl-farms-1-y0zh8xpj (listing LIVE; __NEXT_DATA__ "
               "sites: RV Site 2 Farm View, RV Site 3 Farm View, Blue View RV Site 1, pricePerNight $40.50 each), read " + D},
    {"id": 631, "fees": {
        "nightly_low": 44, "nightly_high": 75, "currency": "USD", "reservation_fee": 6.5,
        "nonresident": {"type": "surcharge", "amount": 8, "per": "stay"}, "checked": "2026",
        "note": ("NOVA Parks' family campground fees, Sunday-Thursday: electric (50/30-amp) $48 April-October and $44 "
                 "November-March, water and electric $55 / $51, full hookup $73 / $68; Friday, Saturday, holidays and "
                 "Sundays before a holiday: $53 / $44, $60 / $51, $75 / $67. The 50 non-electric sites are tent sites "
                 "($37, closed November-March). A one-time $8 per reservation for anyone living outside NOVA Parks' "
                 "member jurisdictions, and a $6.50 transaction fee on online and call-centre bookings (ReserveAmerica). "
                 "The page gives no year. Read " + D + ".")},
     "source": "https://novaparks.com/cabins-camping/camping/camping-family-0 (NOVA Parks 'Camping - Family', Pohick Bay: "
               "'FEES' tables, the $8.00 non-jurisdiction charge and the $6.50 transaction fee), read " + D},
    {"id": 645, "fees": {
        "nightly_low": 110, "nightly_high": 198, "currency": "USD", "checked": "2026",
        "note": ("Daily rates for 2 people by zone: 2026 summer (May 1 - October 31, 2026) Zone D $110, Zone C $120, Zones "
                 "A & B $145; 2025-26 winter (November 1, 2025 - April 30, 2026) $140 / $160 / $180. Campspot's prices for "
                 "a Tuesday and a Saturday in March 2027 (16th and 20th) are 10% above that winter: Zone D $154, full "
                 "hookup $176, waterfront $198. Zone D sites take rigs up to 26 ft. Each extra person $15 a day; at most "
                 "21 days; a 25% deposit; $100 to lock a site; cancelling costs $25. Campspot adds its own booking fee at "
                 "checkout (3%). Read " + D + ".")},
     "source": "https://www.buttonwoodinletrvresort.com/rates/ ('2026 Summer Season', '2025-2026 Season', 'Fees') + "
               "https://www.campspot.com/book/buttonwoodinletrvresort (each RV site type's price breakdown for one night "
               "from 2027-03-16 and from 2027-03-20, 2 adults; family_stays_campspot_2026-10-13.jsonl), read " + D},
    {"id": 240, "fees": {
        "nightly_low": 48, "nightly_high": 60, "currency": "USD", "checked": "2026",
        "note": ("James City County's camping fees, per site per night for up to 6 people (at most 4 adults): water and "
                 "electric $48 (20/30-amp, 50-amp at a few), full hookup $60 - the two site types that take RVs. The $33 "
                 "basic and $36 electric sites, and the $48 'prime' water and electric sites, are for tents and pop-ups. "
                 "Monthly December-February $900. A 2.95% convenience fee on every card payment; cancelling (at least 48 "
                 "hours ahead) costs 10%; Memorial Day and Labor Day weekends take 3 nights. Booked up to a year ahead "
                 "and paid in full (757-258-5020). The page gives no year. Read " + D + ".")},
     "source": "https://www.jamescitycountyva.gov/687/Chickahominy-Riverfront-Park-Fees ('Camping Fees (Daily & "
               "Monthly)', 'Convenience Fee') + https://www.jamescitycountyva.gov/2769/Chickahominy-Riverfront-Park-Rules "
               "('Explanations of Sites According to Campground Map': units allowed per site type), read " + D},
    {"id": 171, "fees": {
        "nightly_low": 24, "nightly_high": 24, "currency": "USD", "checked": "2026",
        "note": ("City of Jacksonville: RV sites $27.24 a night including tax, which is $24.00 plus 13.5% (tents $22.70, "
                 "$20.00 plus 13.5%). Every site has 30/50-amp electric and no water or sewer (water and a dump station "
                 "in the campground); RVs must be self-contained. Pets $5.38 each per stay, three at most; two parking "
                 "passes included, more $5 each. All payments are final, and a cancellation costs one night with tax. "
                 "RVs at most 30 days in any 45. Booked online (the city's WebTrac), by phone (904-255-4255, weekdays) or "
                 "in person. The page gives no year. Read " + D + ".")},
     "source": "https://www.jacksonville.gov/departments/parks-and-recreation/jaxparks/oceanfront-parks/huguenot-memorial-"
               "park ('All fees listed below include tax: Tent fee per night: $22.70 RV fee per night: $27.24 Pet camping "
               "fee: $5.38 per pet, per stay') + the park's rules (https://www.jacksonville.gov/getmedia/acce064d-07b5-442c-"
               "8e77-c38b8bd184b6/Huguenot-Rules-Revised-4-21-26_1.pdf), read " + D},
    {"id": 664, "fees": {
        "nightly_low": 66.99, "nightly_high": 120.99, "currency": "USD", "checked": "2026",
        "note": ("koa.com, one night for 2 adults and a 23-ft motorhome from a Tuesday (2027-06-15) and from a Saturday "
                 "(2027-06-19), before tax: 30-amp water and electric pull-through $66.99 ($75.99 on the Saturday); full "
                 "hookups $67.99-89.99 ($74.99-98.99) by amperage, back-in or pull-through, size and the front row; KOA "
                 "Patio sites $98.99-104.99 ($114.99-120.99). The patio buddy pair, which takes two reservations, is left "
                 "out. Choosing a particular site costs $20 more ('KOA Select My Site'). Read " + D + ".")},
     "source": "https://koa.com/campgrounds/mercer/reserve/ (step 2's 18 site types and their 'avg/night' price for one "
               "night from 2027-06-15 and from 2027-06-19; RV, 2 adults, no pets, a 23-ft motorhome), read " + D},
    {"id": 808, "fees": {
        "nightly_low": 79, "nightly_high": 119, "currency": "USD", "checked": "2026",
        "note": ("koa.com, one night for 2 adults and a 23-ft motorhome, before tax, from a Tuesday and a Saturday in March "
                 "2027 (16th, 20th) and in June 2027 (15th, 19th): back-in 30-amp full hookup $79 on all four; 50/30-amp "
                 "full-hookup pull-throughs $91-101 (Front Circle and buddy sites $91-97); patio pull-throughs $91-105, "
                 "deluxe patio $101-119, lakeside the dearer. March costs more than June, and its Tuesday and Saturday "
                 "matched. Read " + D + ".")},
     "source": "https://koa.com/campgrounds/st-augustine-beach/reserve/ (step 2's 9 site types and their 'avg/night' price "
               "for one night from 2027-03-16, 2027-03-20, 2027-06-15 and 2027-06-19; RV, 2 adults, no pets, a 23-ft "
               "motorhome), read " + D},
    {"id": 807, "fees": {
        "nightly_low": 79, "nightly_high": 98, "currency": "USD", "reservation_fee": 17.5, "checked": "2026",
        "note": ("CampLife (the campground's booking engine; its own site posts no RV rates), one night for 2 adults from "
                 "Tuesday 2027-06-15, quoting 34 of its sites, before tax: back-in sites $79 or $90 a night, pull-throughs "
                 "$98 (tent sites $70); three of them re-quoted from Saturday 2027-06-19 cost the same. Every stay also "
                 "carries a flat $17.50 that the booking pages don't name: one night is the nightly rate plus $17.50 and "
                 "two nights twice the rate plus $17.50; it isn't taxed and isn't in the one-night deposit. Read " + D + ".")},
     "source": "https://www.camplife.com/956/reservation/step1 (the /api/invoice/estimate answer for 34 sites, one night "
               "from 2027-06-15; sites 40, 57 and 111 also one night from 2027-06-19 and two nights from 2027-06-15; 2 "
               "adults) + https://www.artilleryridge.com/camping/ (deposit and cancellation policy, no rates), read " + D},
]

if __name__ == "__main__":
    out = HAND + campspot_findings()
    json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(out), "findings")
    for x in out:
        f = x["fees"]
        print(x["id"], f["nightly_low"], f["nightly_high"], f.get("reservation_fee"), f.get("nonresident"))
