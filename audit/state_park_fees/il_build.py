"""IL findings: IDNR's 2027 camping fee schedule applied to each campground's site classes.

    python3 -I il_build.py OUT

Schedule (dnr.illinois.gov .../2027-camping-changes/fee.pdf, read 2026-10-12): Premium Electric
(formerly AA and A Premium) $35, Electric (formerly A, B/E and B/E Premium) $28, Non-Electric (formerly
B/S, B/S Premium, C and D) $11; electric sites $10 more on the Memorial Day, July 4th and Labor Day
weekends; $10 reservation processing fee; discounts for Illinois seniors and disabled residents only,
no non-resident rate. Site classes: the booking site's unit types per park (il_booking_classes_2026-10-12.json,
ExploreMoreIL search/place for 2027-06-15) and each park's IDNR camping page (il_camp_pages_2026-10-12.json),
which also says which non-electric classes are walk-in or tent sites rather than drive-in ones.

The base is the cheapest site an RV can use: $11 where a drive-in non-electric class exists (B/S,
or a Class C the park describes with vehicle access), otherwise the electric price, with the tent
sites' $11 in the note."""
import json, os, sys
out_path = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
SCHED = "https://dnr.illinois.gov/content/dam/soi/en/web/dnr/parks/2027-camping-changes/fee.pdf"
# id: (classes, extra sentence). Classes: N drive-in non-electric, T tent/walk-in/primitive non-electric,
# E electric ($28), P premium electric ($35), EP = every electric site premium.
C = {
    570: ("P", ""), 779: ("ET", "Its Class C sites are walk-in tent sites."), 791: ("E", ""),
    799: ("ENPT", ""), 1637: ("NP", ""), 1638: ("NEP", "Kankakee's Class C sites at Chippewa have vehicle access."),
    1639: ("NP", ""), 1640: ("ENT", ""), 1641: ("ENT", ""), 1642: ("EN", ""),
    1643: ("N", "Two sites have electric ($28)."), 1644: ("N", ""), 1645: ("E", ""),
    1646: ("ET", ""), 1647: ("P", ""), 1648: ("E", ""), 1649: ("ET", ""),
    1650: ("ET", "Its Class C campground (Turkey Ridge) is walk-in."), 1651: ("ET", ""),
    1652: ("ET", "Its 25 Class B/S sites are tent sites."), 1653: ("ET", ""), 1654: ("EN", ""),
    1656: ("ET", ""), 1658: ("N", "No electric sites."), 1659: ("ET", ""), 1662: ("ENPT", ""),
    1663: ("ET", ""), 1664: ("ET", "Its Class C sites are walk-in tent sites."), 1665: ("E", ""),
    1666: ("ENT", ""), 1667: ("N", "No electric sites; first come, first served."),
    1668: ("ET", ""), 1669: ("EP", ""), 1670: ("ET", ""), 1671: ("ET", ""),
    1673: ("ENT", "Its Class C sites have vehicle access."), 1674: ("ET", ""),
    1676: ("ET", "Its 70 Class B sites are $11 without electric."), 1677: ("EN", ""), 1678: ("P", ""),
    1679: ("EN", ""), 1680: ("ET", ""), 1681: ("EN", ""), 1682: ("ENT", ""), 1683: ("EN", ""),
    1684: ("ENT", ""), 1685: ("ENT", ""), 1686: ("E", ""), 1687: ("ET", ""), 1688: ("EN", ""),
    1689: ("ENT", ""), 1690: ("EPT", "Its 18 Class AA sites have water and sewer."), 1718: ("EP", ""),
    1803: ("ET", "Its Class B tent sites are not reservable."), 1804: ("ENT", ""),
}
PARK = {570: 3, 779: 57, 791: 66, 799: 11, 1637: 10, 1638: 34, 1639: 53, 1640: 41, 1641: 43, 1642: 36, 1643: 69,
        1644: 4, 1645: 46, 1646: 32, 1647: 58, 1648: 49, 1649: 24, 1650: 17, 1651: 19, 1653: 13, 1654: 37, 1656: 18,
        1659: 54, 1662: 14, 1663: 71, 1664: 16, 1665: 50, 1666: 62, 1667: 27, 1668: 55, 1669: 52, 1670: 6, 1671: 65,
        1673: 5, 1674: 12, 1676: 47, 1677: 59, 1678: 61, 1679: 30, 1680: 45, 1681: 35, 1682: 68, 1683: 20, 1684: 39,
        1685: 64, 1686: 67, 1687: 33, 1688: 40, 1689: 57, 1690: 31, 1718: 72, 1803: 48, 1804: 26}
TAIL = (" Electric sites $10 more on the Memorial Day, July 4th and Labor Day weekends. $10 reservation fee (it was $5 "
        "through 2026). No out-of-state rate; Illinois seniors and disabled residents get discounts. IDNR's 2027 camping "
        "fee schedule, read {d}, applied to this campground's site classes.")
out = []
for eid, (cls, extra) in sorted(C.items()):
    s = {}
    if "N" in cls:
        low = 11
        if "E" in cls and "P" in cls:
            s = {"electric": 17, "premium_site": 7}
            text = "$11 a night for a site without electric; electric $28; premium electric $35."
        elif "E" in cls:
            s = {"electric": 17}
            text = "$11 a night for a site without electric; electric $28."
        elif "P" in cls:
            s = {"electric": 24}
            text = "$11 a night for a site without electric; electric $35 (every electric site here is a premium one)."
        else:
            text = "$11 a night (no electric)."
    elif "E" in cls:
        low = 28
        if "P" in cls:
            s = {("full_hookup" if eid == 1690 else "premium_site"): 7}
            text = "$28 a night for an electric site; premium electric (Class AA) $35."
        else:
            text = "$28 a night; every RV site has electric."
        if "T" in cls:
            text += " Tent and walk-in sites without electric are $11."
    else:
        low = 35
        text = "$35 a night; every site is a premium electric site."
    if extra:
        text += " " + extra
    fees = {"nightly_low": low, "nightly_high": low, "currency": "USD", "reservation_fee": 10}
    if s:
        fees["surcharges"] = s
    fees["checked"] = "2026"
    fees["note"] = text + TAIL.format(d=D)
    pid = PARK.get(eid)
    src = (f"{SCHED} (2027 schedule: Premium Electric $35, Electric $28, Non-Electric $11, $10 reservation fee, read {D})"
           + (f" + recreation.exploremoreil.com park {pid} site classes (search/place for 2027-06-15, read {D})" if pid else "")
           + f" + {rows[eid]['website'].split()[0]} (the park's camping page, read {D})")
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees, "source": src})
# Illinois State Fairgrounds: Department of Agriculture, its own rate table.
out.append({"id": 1719, "name": rows[1719]['name'], "fees": {
    "nightly_low": 35, "nightly_high": 35, "currency": "USD", "checked": "2026",
    "note": ("$35 a night for a site with electric and water (April-October except August); $40 in the Memorial Day and "
             "Labor Day weeks; tent sites $25; campers 60 and older and veterans $30; sites outside the main campground "
             f"$40; $50 during the State Fair in August. No reservations: first come, first served. Fairgrounds' "
             f"campground page, read {D}.")},
    "source": f"https://statefair.illinois.gov/non-fair-events/facilities/campgrounds.html (Rates (April - October), read {D}) "
              f"+ https://statefair.illinois.gov/info/camping.html (State Fair camping $50, read {D})"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'IL findings')
for x in out:
    print(x['id'], x['name'][:40], x['fees']['nightly_low'], x['fees'].get('surcharges'))
