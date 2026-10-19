#!/usr/bin/env python3
"""AWH's answers to the 2026-10-19 open list, plus the items handled under standing rules.

Run once: drops are logged to ../dropped_2026-10-19.jsonl and removed; prices and notes
are set from the operator pages already captured under audit/price_research/.
"""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 2)[0])
from edit_entries import edit, P

ROOT = P.rsplit("/", 1)[0]
LOG = ROOT + "/audit/price_research/dropped_2026-10-19.jsonl"

DROPS = {
    1297: "AWH 2026-10-19: festival / swimming-quarry venue, not a campground for us",
    5843: "AWH 2026-10-19: Bible camp's RV sites serve its camps and conferences",
    5336: "AWH 2026-10-19: RV sites belong to a shooting complex",
    14482: "AWH 2026-10-19: Quaker youth camp, no public nightly RV camping posted",
    1381: "AWH 2026-10-19: seasonal-site park, no nightly rate posted",
    1261: "AWH 2026-10-19: not operating as a campground (latest report: 'a neighborhood, not a campground')",
    6690: "AWH 2026-10-19: reported permanently closed; no website or phone",
    6167: "AWH 2026-10-19: RV Life marks it closed; no 2026 activity",
    13351: "AWH 2026-10-19: rate visible only in the reservation cart; the site is a hassle to use",
    14400: "membership park: the page is a Thousand Trails membership offer only (membership parks are out)",
    14405: "membership park: the page is a Thousand Trails membership offer only (membership parks are out)",
    14417: "membership park: the page is a Thousand Trails membership offer only (membership parks are out)",
    14984: "long-stay test: one nightly RV site, the rest seasonal (fewer than 1 in 10 nightly)",
    1376: "long-stay test: weekly/monthly stays only, by application",
    10581: "over the USD gate: base USD 55 for 2 adults (own rate page, 'Updated 4/1/2024'; AWH counts 2024 rates); no gateway within 40 km, no named exception",
    14410: "over the USD gate: base USD 75 (own page, '2024 Rates'; AWH counts 2024 rates); no gateway within 40 km, no named exception",
    7249: "inclusion: FCWD lists Guthrie Park as a 'Primitive Camping Park'; its policy puts every camper on an RV site and RV sites are at Walleye Park, while 'all other parks are rough tent camping' ($10 per tent) -> tent-only. Its fees were Walleye's",
    7285: "inclusion: FCWD lists Overlook Park as a 'Primitive Camping Park' -> rough tent camping only, per the district's reservation policy. Its fees were Walleye's",
}


def fees(lo, hi, cur, note, src, read):
    def f(e):
        e["fees"] = {"nightly_low": lo, "nightly_high": hi, "currency": cur, "checked": "2026", "note": note}
        e.setdefault("provenance", {})["fees"] = {"source": src, "checked": read}
        return e
    return f


def chain(*fs):
    def f(e):
        for g in fs:
            e = g(e)
        return e
    return f


def note_replace(old, new):
    def f(e):
        assert old in e["note"], (e["id"], old)
        e["note"] = e["note"].replace(old, new)
        return e
    return f


def fcfs(e):
    e["booking"] = {"reservable": False, "fcfs": "always"}
    return e


def walleye_booking(e):
    b = e.get("booking") or {}
    b.update({"reservable": True, "platform": "operator",
              "min_stay": [{"nights": 3, "applies": "always"}],
              "note": "Reservations need 3 nights and open 60 days ahead; a walk-up may take any non-reserved RV site and pay the camp host (FCWD reservation policy, read 2026-10-19)."})
    e["booking"] = b
    return e


FNS = {
    3019: chain(fees(20, 20, "USD", "2024 season rate: $20 a night per camper pad; first come, first served.",
                     "https://rockrapids.com/to-do-see/camping-cabins/ ('2024 Camping season will be $20.00 per night per camping pad', read 2026-10-17)", "2026-10-17"),
                fcfs, note_replace("Contact city for rates/reservations.", "No reservations: first come, first served, $20 a pad (2024 season rate).")),
    9106: fees(25, 40, "CAD", "2024 season rates: power-and-water sites C$40, unserviced pull-throughs C$25.",
               "https://oldslionsclub.com/OldsLionsCampground.htm ('2024 Season Site Rates ... RV Sites (Power & Water Only) - $40.00/night ... Pull through sites (No power or water) - $25.00/night', read 2026-10-15)", "2026-10-15"),
    8113: fees(40, 40, "USD", "2024 rates (effective 1 March 2024): $40 a night with water, electric and sewer, tax included.",
               "https://pietownrvpark.com/rates ('2024 Rates | NOTICE: Effective 1 March 2024 | Daily Rate: $40', read 2026-10-16)", "2026-10-16"),
    10571: fees(42, 47, "USD", "2024 rates: full hookup $42 (30A), $47 (50A).",
                "http://www.lighthousebythebay.com/p3_rates.php ('2024-rates | Daily Full hookup $42 30amp | $47 50amp', read 2026-10-16)", "2026-10-16"),
    14654: fees(44, 44, "USD", "Overnight with full hookups $44 for two people (rates effective August 1, 2024); military $35.",
                "https://southgatervpark.com/rates-and-reservations/ ('Rates (effective August 1, 2024): Overnight with full hookups: $44.00 - for 2 people', read 2026-10-16)", "2026-10-16"),
    14783: fees(41, 41, "USD", "2024 RV rates: daily $41, seventh night free.",
                "https://www.bedrockrv.com/ ('2024 RV Rates | Daily - $41', read 2026-10-16)", "2026-10-16"),
    14416: fees(100, 100, "USD", "2024-25 season (Nov 1 - Apr 30): daily $100. Over the gate; kept as within 40 km of St. Petersburg.",
                "https://www.fiestagroverv.com/rates/ ('2024-2025 Season | November 1, 2024 - April 30, 2025 | Daily: $100.00', read 2026-10-16)", "2026-10-16"),
    11604: fees(45, 65, "USD", "2025 rates: one night $45 plus tax ($65 in January); no electric charge on 1-2 night stays.",
                "https://www.parkplacervpark.net/rates-booking/ ('RATES for 2025 ... January Nightly $65 + Tax | 1 Night $45 + Tax', read 2026-10-16)", "2026-10-16"),
    12854: fees(42, 60, "CAD", "Unserviced C$42, two services C$50-55, three services C$60, plus HST, for 2 adults and 2 kids; online bookings add C$3 for a 1-night stay.",
                "https://campingstbasile.com/ ('None-Serviced $42 + hst | 2-Services Starts at $50-$55 + hst | 3-Services Starts at $60 + hst', read 2026-10-16)", "2026-10-16"),
    4359: note_replace("Dorchester/Ridgeville area.", "Dorchester/Ridgeville area. Rigs must be no more than 15 years old."),
    8096: note_replace("(18+, 2-night minimum, cash/check)", "(adults 18+, 2-night minimum, cash/check). AGE-RESTRICTED: the posted rates are for two people over 55"),
    8125: note_replace("Small adults-only (30+) RV park", "AGE-RESTRICTED: adults only, and at least one guest must be 30+. Small RV park"),
    7325: walleye_booking,
}

cur = {e["id"]: e for e in json.load(open(P))}
with open(LOG, "a") as log:
    for i, why in DROPS.items():
        e = cur[i]
        log.write(json.dumps({"id": i, "name": e["name"], "state": e["state"], "ownership": e["ownership"],
                              "action": "removed", "why": why}, ensure_ascii=False) + "\n")
        FNS[i] = lambda e: None
edit(FNS)
print("dropped", len(DROPS), "edited", len(FNS) - len(DROPS))
