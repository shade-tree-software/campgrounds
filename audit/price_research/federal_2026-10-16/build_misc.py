#!/usr/bin/env python3
"""Federal leftovers off fs.usda.gov / rec.gov (BLM, NPS, LBL, refuges, MWR), read by hand
from each operator page on 2026-10-16 (site_digest.py -> digest.txt) -> misc_findings.json.

Rules as elsewhere: the range runs from the cheapest to the dearest site a drive-in RV can
use; an entrance fee is not a camping fee; tent-only, group and cabin rates are left out.
"""
import json
B = "https://www.blm.gov/visit/"
LBL = "https://www.landbetweenthelakes.us/"
YELL = "https://www.nps.gov/yell/planyourvisit/campgrounds.htm"
JOTR = "https://www.nps.gov/jotr/planyourvisit/campgrounds.htm"
SS = LBL + "facility/self-service-camping/"
ROWS = [  # id, url, low, high, quote, note
 (684, LBL + "visit/hillman-ferry-campground/", 12, 42, "Basic Nightly Rate $12 ... 50 Amp Electric/Water/Sewer Nightly Rate $42", "Basic $12; 30A electric $26; electric/water $34-36; full hookup $40-42."),
 (685, LBL + "visit/piney-campground/", 12, 42, "Basic Nightly Rate $12 ... 50 Amp Electric/Water/Sewer Nightly Rate $42", "Basic $12; 30A electric $26; full hookup $40-42."),
 (1584, LBL + "visit/energy-lake-campground/", 12, 28, "Basic Nightly Rate $12 | 30 Amp Electric Nightly Rate $26 | 50 Amp Electric Nightly Rate $28", "Basic $12; electric $26-28."),
 (1585, SS, 10, 10, "Redd Hollow – $10 per night", None),
 (1586, SS, 10, 10, "Taylor Bay – $10 per night", None),
 (4438, SS, 10, 10, "Boswell Landing – $10 per night", None),
 (4441, SS, 10, 10, "Gatlin Point – $10 per night", None),
 (6074, B + "divide-bridge-campground", 15, 15, "Divide Campground--15$ / night April 1 - November 30", None),
 (6078, B + "carbella-rec-site", 15, 15, "15$ per night per campsite, April 1 to November 30", None),
 (6079, B + "james-kipp-campground", 20, 20, "$20.00 per night, 14 Day stay limit", None),
 (6082, B + "galena-gulch-campground", 10, 10, "10$ / night, April 1 to November 30.", None),
 (6104, B + "camp-creek-campground", 10, 10, "$10/night for camping at Camp Creek and Horse Corral", None),
 (6107, B + "montana-gulch", 8, 8, "Fees | $8/Night", None),
 (6362, B + "atlantic-city-campground", 20, 20, "$20 per night. No reservations first come first serve.", None),
 (6371, B + "cottonwood-campground-0", 20, 20, "$20 per night. No reservations first come first serve.", None),
 (6373, B + "big-atlantic-gulch-campground-0", 20, 20, "$20 per night. No reservations first come first serve.", None),
 (6374, B + "encampment-river-campground", 10, 10, "Camping fees are $10 per campsite per night.", None),
 (6384, YELL, 38, 38, "Bridge Bay | 5/15 – 9/13 | $38 + taxes", "2026 rate, plus taxes."),
 (6385, YELL, 45, 45, "Canyon | 5/29 – 9/19 | $45 + taxes", "2026 rate, plus taxes."),
 (6390, YELL, 94, 94, "Fishing Bridge RV Park | 5/8 – 10/17 | $94 + taxes", "2026 rate, plus taxes; full hookups."),
 (6393, YELL, 45, 45, "Grant Village | 6/26 – 9/26 | $45 + taxes", "2026 rate, plus taxes."),
 (6396, YELL, 20, 20, "Indian Creek | 6/12 – 9/14 | $20", None),
 (6397, YELL, 20, 20, "Lewis Lake | 6/15 – 10/11 | $20", None),
 (6399, YELL, 38, 38, "Madison | 5/1 – 10/17 | $38 + taxes", "2026 rate, plus taxes."),
 (6400, YELL, 25, 25, "Mammoth | Open year-round* | $25", None),
 (6637, "https://sill.armymwr.com/programs/letra", 50, 50, "LETRA RV Site Rates: | Monthly Rate: $500 | Weekly Rate: $200 | Daily Rate: $50", "Weekly $200, monthly $500."),
 (7106, "https://www.fws.gov/refuge/buffalo-lake/visit-us", 2, 2, "Camping fees are $2 per vehicle/per day.", None),
 (7151, "https://www.nps.gov/pais/planyourvisit/fees.htm", 0, 0, "The fee for dispersed beach camping is included with your valid 7-Day, Annual, or Lifetime park entrance pass.", "No camping fee; a park entrance pass is required."),
 (7955, B + "datil-well-recreation-area-campground", 20, 30, "$20/night for campsites without electric. | $30/night for campsites with electric.", None),
 (7961, B + "three-rivers-petroglyph-site", 25, 25, "RV Hookup (per campsite): $25", "Tent/shelter sites $10."),
 (7972, B + "aguirre-spring-campground", 7, 7, "Overnight Camping fee is $7 per vehicle per campsite.", None),
 (7976, B + "orilla-verde-recreation-area", 7, 7, "$7 /night developed campsites | $15 /night RV site", "Developed sites $7; the area's RV (hookup) sites are $15."),
 (7981, B + "wild-rivers-recreation-area", 7, 7, "Camping : $7.00/night for up to two vehicles.", None),
 (7984, B + "santa-cruz-lake-recreation-area", 9, 9, "Camping $9 per night first come first-served", None),
 (9710, B + "lud-drexler-park", 15, 15, "Camping Fee: $15/night, includes two vehicles.", None),
 (9719, B + "cove-recreation-site", 15, 15, "Camping: $15 per campsite/night.", None),
 (9734, B + "steck-park", 8, 8, "RV-$8.00/night; tent-$5.00/night", None),
 (9744, B + "cottonwood-recreation-site", 10, 10, "Campsites: $10 per night", None),
 (9763, B + "killarney-lake-campground-access", 20, 20, "$20 Occupancy Fee.", None),
 (9887, "https://www.lakepowell.com/stay/rv-camping/bullfrog-rv-campground", 60, 60, "Daily price of $60 + tax.", "Plus tax; full hookups."),
 (9904, B + "calf-creek-recreation-area-campground", 15, 15, "$15.00 per campsite per night", None),
 (9905, B + "starr-springs-campground", 10, 10, "$10 per day camping fee", None),
 (9938, B + "horsethief-campground", 20, 20, "$20.00 per site per night camping fee", None),
 (9942, B + "drinks-canyon-camping-area", 20, 20, "Fees | $20/night", None),
 (9943, B + "hal-canyon-campground", 20, 20, "Fees | $20/night", None),
 (9972, B + "price-canyon-recreation-area", 15, 15, "$15 per site per night", None),
 (10562, "https://www.nps.gov/laro/planyourvisit/fees.htm", 30, 30, "Keller Ferry (Operated by Lake Roosevelt Adventures) : $30 per site per night", None),
 (10695, B + "gerber-recreation-area", 7, 7, "Fees - $7 per night, $4 per extra vehicle", None),
 (10797, B + "page-springs-campground", 16, 16, "Camping Fees are $16/vehicle, per night, for a single car, truck, or RV and towed vehicle.", None),
 (10812, B + "macks-canyon-recreation-site", 8, 12, "Weekdays: $8.00 per night | Weekends*: $12.00 per night", "$12 Friday and Saturday nights June 1-Sep 15, else $8."),
 (10852, B + "chukar-park-campground", 5, 5, "Fees | $5 per night.", None),
 (10853, B + "topsy-campground", 7, 7, "$7 per night, $4 per extra vehicle", None),
 (10885, B + "trout-creek-campground", 8, 12, "Weekdays: $8.00 per night | Weekends*: $12.00 per night", "$12 Friday and Saturday nights June 1-Sep 15, else $8."),
 (10928, B + "chimney-rock-campground", 8, 8, "$8 per single campsite per night", None),
 (10948, B + "chickahominy-recreation-site", 16, 16, "Camping Fees are $16/vehicle, per night", None),
 (10972, B + "sixes-river-campground", 16, 16, "Camping | $16.00 Single Campsite", None),
 (11003, B + "dovre-recreation-site", 15, 15, "Campsite fee of $15 per night includes one vehicle per site.", None),
 (11228, B + "tabor-creek-campground", 5, 5, "$5.00 per vehicle per day for Camping.", None),
 (11240, B + "walker-lake-recreation-area", 6, 6, "Developed Camp Site: $6/night/vehicle $36/week/vehicle", "Primitive camp area $4/night."),
 (11319, "https://navajonationparks.org/navajo-tribal-parks/tseyi-dine-heritage-area/", 30, 30, "Camping: $30.00/per night (up to 7 people) FIRST COME, FIRST SERVED.", None),
 (11320, "https://willowbeachharbor.com/campground-rv-park/", 80, 80, "Nightly | $80", "RV sites; tent sites $45."),
 (11325, B + "la-posa-long-term-visitor-area", 15, 15, "From April 16th through September 14th, the fee is ... $15 per vehicle for overnight use", "Apr 16-Sep 14. In the LTVA season (Sep 15-Apr 15) a permit: $40 for 14 days or $180 for the season."),
 (11329, B + "painted-rock-petroglyph-campground", 8, 8, "$8.00 per vehicle per night", None),
 (11399, B + "owl-creek-campground", 5, 5, "The fee for overnight use, with two vehicles per night, is currently $5.", None),
 (11401, B + "oxbow-recreation-and-wildlife-area", 15, 15, "$15 for overnight use", None),
 (11429, B + "fourmile-canyon-campground", 5, 5, "The fee for overnight use, with two vehicles per night, is currently $5.", None),
 (12025, JOTR, 25, 25, "Belle | 18 sites. $25 per night.", None),
 (12027, JOTR, 25, 25, "White Tank | 15 sites. $25 per night.", None),
 (12028, JOTR, 25, 25, "Hidden Valley | 44 sites. $25 per night.", None),
 (12310, B + "wailaki-campground", 15, 15, "$15.00 per campsite per night", None),
 (12311, B + "tolkan-campground", 15, 15, "$15.00 per night for campsites", None),
 (12312, B + "mattole-campground", 15, 15, "Use Fee: Camping - $15.00", None),
 (12316, B + "pit-river-campground", 8, 8, "$8.00 Daily Camping fee.", None),
 (12318, B + "north-eagle-lake-campground", 8, 8, "The fee is $8 per night for a single site or $11 per night for multiple occupancy.", None),
 (12329, B + "fossil-falls-campground", 6, 6, "The fee is $6.00 per night", None),
 (12338, B + "afton-canyon", 6, 6, "Fees | $6 per night", None),
 (12344, B + "corn-springs-campground", 6, 6, "a $6.00 per night camping fee", None),
 (12348, B + "imperial-dam-long-term-visitor-area", 15, 15, "From April 16th through September 14th, the fee is ... $15 per vehicle for overnight use", "Apr 16-Sep 14. In the LTVA season (Sep 15-Apr 15) a permit: $40 for 14 days or $180 for the season."),
]
F = []
for i, url, lo, hi, quote, note in ROWS:
    fees = {"nightly_low": lo, "nightly_high": hi}
    if hi:
        fees["currency"] = "USD"
    if note:
        fees["note"] = note
    F.append({"id": i, "fees": fees, "source": f"{url} ('{quote}', read 2026-10-16)"})
json.dump(F, open("misc_findings.json", "w"), indent=1, ensure_ascii=False)
print(len(F))
