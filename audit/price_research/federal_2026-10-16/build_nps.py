#!/usr/bin/env python3
"""NPS campgrounds whose fee the park page draws by script, read in the driver browser
(rendered 'Fees' block) on 2026-10-16 -> nps_findings.json. Julian Price via its rec.gov
facility (recgov_sites.py, nps_sites.json); entrance fees are not camping fees."""
import json
N = "https://www.nps.gov/"
EV = N + "ever/planyourvisit/camping.htm"
ROWS = [
 (34, "https://www.recreation.gov/camping/campgrounds/234037", 30, 30, "per-campsite rates: STANDARD/RV NONELECTRIC $30", None),
 (49, N + "natr/planyourvisit/camping.htm", 0, 0, "Fees ... $0.00", None),
 (498, N + "neri/planyourvisit/army-camp-campground.htm", 0, 0, "There are no fees for camping.$0.00", None),
 (679, EV, 33, 60, "Flamingo Campground- tent and non-electric RV (Monday - Thursday ...) $33.00 ... RV with electric hookup (Friday - Sunday ...) $60.00", "Non-electric $33 Mon-Thu / $38.50 Fri-Sun; electric $50 / $60."),
 (2315, N + "cure/planyourvisit/camp_dry_gulch.htm", 20, 20, "The nightly camping fee at Dry Gulch is $20.00.", None),
 (4741, EV, 33, 38.5, "Long Pine Key Campground- tent and non-electric RV (Monday - Thursday ...) $33.00 ... (Friday - Sunday ...) $38.50", "$33 Mon-Thu, $38.50 Fri-Sun."),
 (7093, N + "amis/planyourvisit/277-north-campground.htm", 6, 6, "277 North Campground Standard Site, Nightly Rate $6.00", None),
 (7094, N + "amis/planyourvisit/governors-landing-campground.htm", 10, 10, "Governors Landing Campground Standard Site, Nightly $10.00", None),
 (7095, N + "amis/planyourvisit/rough-canyon-campground.htm", 6, 6, "Rough Canyon Campground Standard Site, Nightly $6.00", None),
 (7096, N + "amis/planyourvisit/san-pedro-campground.htm", 6, 6, "San Pedro Campground Standard Site, Nightly $6.00", None),
 (7097, N + "amis/planyourvisit/spur-406-campground.htm", 6, 6, "Spur 406 Campground Standard Site, Nightly $6.00", None),
 (7171, N + "bibe/planyourvisit/rgv_hookups.htm", 36, 36, "RV camping fee $36 double occupancy, with a $3 per additional person charge.", "Full hookups; two people, $3 per additional person."),
 (9471, N + "crmo/planyourvisit/camping.htm", 15, 15, "Campground Fee - Regular Season ... $15.00 ... Shoulder Season ... $8.00", "May-Oct; $8 in April and November when the water is off."),
 (12021, N + "deva/planyourvisit/sunset-campground.htm", 18, 18, "Sunset Campground ... Standard Rate ... $18.00", None),
 (12022, N + "deva/planyourvisit/stovepipe-wells-campground.htm", 18, 18, "Stovepipe Wells ... $18.00", None),
 (12023, N + "deva/planyourvisit/mesquite-spring-campground.htm", 20, 20, "Mesquite Campground Fee - Standard Rate ... $20.00", None),
 (12401, N + "deva/planyourvisit/texas-springs-campground.htm", 20, 20, "Texas Spring Camping ... Standard Rate ... $20.00", None),
]
F = []
for i, url, lo, hi, quote, note in ROWS:
    fees = {"nightly_low": lo, "nightly_high": hi}
    if hi:
        fees["currency"] = "USD"
    if note:
        fees["note"] = note
    F.append({"id": i, "fees": fees, "source": f"{url} ('{quote}', read 2026-10-16)"})
json.dump(F, open("nps_findings.json", "w"), indent=1, ensure_ascii=False)
print(len(F))
