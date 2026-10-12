"""Saskatchewan entries on provincial land that their operators price themselves, each from its own rates page, read
2026-10-12 (page text in sk_operator_pages_2026-10-12.json).

    python3 -I sk_other_build.py OUT

- Borden Bridge Campground (leased, in the Borden Bridge Recreation Site): '2026 Camping Rates'.
- Michel Point Campground & RV Park (private, at Dore Lake): its rates block, the same nightly rates as its '2025 Rates'.
- Nesslin Lake Campground (leased Nesslin Lake Recreation Site): its non-powered and powered camping pages, which say
  the powered sites are fully booked for the 2026 season.
Besant Campground is not priced: Facebook and a phone number only, no rate published."""
import json, sys
D = "2026-10-12"
out = [
    {"id": 9292, "name": "Borden Bridge Campground", "fees": {
        "nightly_low": 25, "nightly_high": 25, "currency": "CAD", "surcharges": {"electric": 10}, "checked": "2026",
        "note": ("2026 rates: non-electric sites $25 a night ('a handful of non-electric sites for tents and smaller self "
                 "contained campers'), electric sites with water $35; weekly, monthly and seasonal rates too. Gate entry "
                 f"$10 a day; showers $2. The campground's rates page, read {D}.")},
     "source": f"https://bordenbridgecampground.ca/prices/ ('2026 Camping Rates'), read {D}"},
    {"id": 9303, "name": "Michel Point Campground & RV Park", "fees": {
        "nightly_low": 35, "nightly_high": 35, "currency": "CAD", "surcharges": {"full_hookup": 10}, "checked": "2026",
        "note": ("'Power & Water: $35/night'; 'Power, Water & Sewer: $45/night' (30-amp sites; 'Site rates include 4 "
                 "adults'), the same nightly rates as its 2025 list; monthly and seasonal rates too. Open May long "
                 f"weekend to September 30. Its rates page, read {D}.")},
     "source": f"https://michelpointcampground.ca/campground.htm (camping rates), read {D}"},
    {"id": 9304, "name": "Nesslin Lake Campground", "fees": {
        "nightly_low": 28, "nightly_high": 28, "currency": "CAD", "surcharges": {"electric": 10}, "checked": "2026",
        "note": ("Non-powered sites $28 + tax a night ('Perfect for tents and RVs of all sizes'; water at stations); "
                 "powered sites (30 amp, with water, trailers to 40 ft) $38 + tax, 'FULLY BOOKED FOR 2026 SEASON'. Its "
                 f"camping pages, read {D}.")},
     "source": f"https://www.nesslinlake.com/motorhome (non-powered) + https://www.nesslinlake.com/copy-of-non-powered-camping "
               f"(powered), read {D}"},
]
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "findings")
