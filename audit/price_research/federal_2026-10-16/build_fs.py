#!/usr/bin/env python3
"""Forest Service leftovers, read by hand 2026-10-16 -> fs_hand_findings.json for ../apply.py.

Sources: each campground's fs.usda.gov 'Fee Site and Info' block (trip_data/fs_fees.json via
fs_fees.py, or the page found through the forest sitemap, fs_sitemap.json), and the Sawtooth
NRA's one fee schedule (sawtooth_fees.json) for the SNRA campgrounds, including the ones whose
rec.gov listing is a rate-less POI page.

Pass-only sites (no camping fee; a vehicle pass covers overnight use) are priced at what
one night costs, the SB Cove 11415 precedent: the pass's price, said in the note.
"""
import json
FS = "https://www.fs.usda.gov/"
SNRA = json.load(open("sawtooth_fees.json"))
ROWS = [  # id, url, low, high, quote, note
 (83, FS + "r09/monongahela/recreation/stuart-day-use-area-and-campground", 33, 33, "Single Site: $33 per night | Double Site: $58 per night", "Double sites $58."),
 (2764, FS + "r02/nebraska/recreation/toadstool-geological-park-and-campground", 15, 15, "Single Site: $15 per night (1 vehicle include per site)", None),
 (7136, FS + "r03/cibola/recreation/lake-marvin-campground", 20, 20, "Single Site with electric hook-up: $20 per night | No fee for tent camping", "Electric sites $20; tent camping free."),
 (11994, FS + "r05/inyo/recreation/deadman-campground-upper-and-lower", 0, 0, "No fees are required for this site", None),
 (12032, FS + "r05/six-rivers/recreation/e-ne-nuck-campground", 10, 10, "Camping: $10 per night", None),
 (12035, FS + "r05/six-rivers/recreation/big-flat-campground", 8, 8, "$8 per vehicle per day | Additional Vehicle Fee: $5 per vehicle per night", "$8 per vehicle; extra vehicle $5."),
 (12037, FS + "r05/six-rivers/recreation/grassy-flat-campground", 10, 10, "$10 per campsite | Includes one vehicle", None),
 (12038, FS + "r05/mendocino/recreation/bear-creek-campground", 0, 0, "No fees are required for this site", None),
 (12079, FS + "r05/shasta-trinity/recreation/deadlun-campground", 0, 0, "No fees are required for this site", None),
 (12081, FS + "r05/shasta-trinity/recreation/cattle-camp-campground", 15, 15, "Single Site: $15 per night", None),
 (12082, FS + "r05/shasta-trinity/recreation/harris-spring-campground", 0, 0, "Fee Site and Info | Free", None),
 (12084, FS + "r05/modoc/recreation/blanche-lake-campground", 0, 0, "No fees are required for this site", None),
 (12085, FS + "r05/modoc/recreation/bullseye-lake-campground", 0, 0, "Fee Site and Info | None", None),
 (12214, FS + "r05/modoc/recreation/plum-valley-campground", 0, 0, "Fee Site and Info | none", None),
 (12184, FS + "r05/eldorado/recreation/jones-fork-campground", 10, 10, "$10/single family site | $5/extra vehicle fee", None),
 (12189, FS + "r05/eldorado/recreation/big-meadows-campground", 10, 10, "$10/ single site | $20/ double site", "Double sites $20."),
 (12242, FS + "r05/inyo/recreation/big-meadow-campground", 35, 35, "Single Site: $35 per night", None),
 (12243, FS + "r05/inyo/recreation/iris-meadow-campground", 35, 35, "Single Site: $35 per night", None),
 (12247, FS + "r05/inyo/recreation/holiday-campground", 35, 35, "Single Site: $35 per night", None),
 (12248, FS + "r05/inyo/recreation/lake-george-campground", 34, 34, "Single Site: $34 per night", None),
 (12273, FS + "r05/sequoia/recreation/south-fork-rec-campground", 12, 12, "$12.00 Per night camping fee", None),
 (12269, FS + "r05/sequoia/recreation/old-isabella", 12, 12, "Camping fee, $12.00 per night", None),
 (12286, FS + "r05/inyo/recreation/grandview-campground", 0, 0, "No fees are required for this site | Maintenance donation of $10.00 per night", "No fee; a $10/night maintenance donation is asked."),
 (12004, FS + "r05/angeles/recreation/monte-cristo-campground", 20, 20, "Single Site: $20 per night", None),
 (9980, FS + "r04/uinta-wasatch-cache/recreation/vernon-reservoir-campground-day-use-fishing-area", 10, 10, "Day Use/Overnight: | $10 per vehicle per three day", "No camping fee: a vehicle pass covers overnight use, $10 for three days or $20 for seven."),
 (9981, FS + "r04/uinta-wasatch-cache/recreation/unicorn-ridge-campground", 10, 10, "Day Use/Overnight: | $10 per vehicle per three day", "No camping fee: a vehicle pass covers overnight use, $10 for three days or $20 for seven."),
 (9987, FS + "r04/uinta-wasatch-cache/recreation/sawmill-hollow-campground", 10, 10, "Day Use/Overnight: | $10 per vehicle per three day", "No camping fee: a vehicle pass covers overnight use, $10 for three days or $20 for seven."),
 (10119, FS + "r04/uinta-wasatch-cache/recreation/salamander-flat-campground", 10, 10, "Day Use/Overnight: | $10 per vehicle per three day", "No camping fee: a vehicle pass covers overnight use, $10 for three days or $20 for seven."),
 (10231, FS + "r06/mbs/recreation/ranger-creek-campground", 5, 5, "A $5 per vehicle per day or valid recreation pass required at the campground", "No camping fee: $5 per vehicle per day, or a recreation pass."),
 (10240, FS + "r06/okanogan-wenatchee/recreation/taneum-junction-campground", 5, 5, "Day and Overnight Use: | $5 per vehicle per day", "No camping fee: $5 per vehicle per day (Scan & Pay), or $30 a year."),
 (11383, FS + "r03/tonto/recreation/bermuda-flat-shoreline-area", 8, 12, "$8 per vehicle per day (purchased at Tonto NF Office or Retail Vendor) | $12 per vehicle per day (purchased on-site", "No separate camping fee: a Tonto Pass per vehicle per day, $8 from an office or vendor, $12 from the on-site machine."),
 (11403, FS + "r03/tonto/recreation/bartlett-flat-shoreline-area", 8, 12, "$8 per vehicle per day (purchased at Tonto NF Office or Retail Vendor) | $12 per vehicle per day (purchased on-site", "No separate camping fee: a Tonto Pass per vehicle per day, $8 from an office or vendor, $12 from the on-site machine."),
 (11965, FS + "r05/lospadres/recreation/valle-vista-campground", 5, 5, "Adventure Pass ($5/day or $30/year) ... required", "No camping fee: an Adventure Pass ($5/day, $30/year) or interagency pass."),
 (12146, FS + "r05/lospadres/recreation/bates-canyon-campground", 5, 5, "The Adventure Pass or Annual Interagency Pass ... is required", "No camping fee: an Adventure Pass ($5/day, $30/year, per the Los Padres pages) or interagency pass."),
]
SNRA_IDS = {9498: "Wood River Campground", 9503: None, 9511: "North Shore Campground", 9500: "Murdock Campground",
            9516: "Pettit Lake Campground", 9524: "Mount Heyburn Campground", 9526: "Sockeye Campground",
            9529: "Grandjean Campground", 9530: "Chinook Bay Campground", 9534: "Iron Creek Campground",
            9538: "Holman Creek Campground", 9539: "Salmon River Campground", 9541: "Lower O'Brien Campground",
            9542: "Upper O'Brien Campground", 9543: "Mormon Bend Campground", 9547: "Riverside Campground"}
F = []
for i, url, lo, hi, quote, note in ROWS:
    fees = {"nightly_low": lo, "nightly_high": hi}
    if hi:
        fees["currency"] = "USD"
    if note:
        fees["note"] = note
    F.append({"id": i, "fees": fees, "source": f"{url} ('{quote}', read 2026-10-16)"})
for i, name in SNRA_IDS.items():
    # Caribou appears twice in the schedule; the Wood River section's row is $20 ("Caribou Campground |
    # Single Family -- per campsite, one vehicle, per night | $20"), the later $14 row is another Caribou.
    v = 20 if name is None else SNRA["single_family"][name]
    F.append({"id": i, "fees": {"nightly_low": v, "nightly_high": v, "currency": "USD"},
              "source": f"{SNRA['url']} ('{name or 'Caribou Campground'} | Single Family -- per camp unit, per night | ${v}', read 2026-10-16)"})
json.dump(F, open("fs_hand_findings.json", "w"), indent=1, ensure_ascii=False)
print(len(F))
