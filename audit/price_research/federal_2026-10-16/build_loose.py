#!/usr/bin/env python3
"""Loose ends of the federal pass, 2026-10-16 -> loose_findings.json. Agency pages read in the
driver browser (BLM, NPS rendered Fees), the NPS campgrounds API (developer.nps.gov, the data the
park pages render), RIDB FacilityUseFeeDescription, and the Federal Register for Wilson Lake."""
import json
ROWS = [
 (6085, "https://www.blm.gov/announcement/blm-increase-campground-fees-enhance-visitor-experience-along-madison-river", 20, 20, "BLM 2025-03-31 table: Ruby Creek Campground current $12/night, new fee $20/night; Campendium 2026 camper report: $20 in 2026", None),
 (6099, "https://www.blm.gov/visit/departure-point", 15, 15, "Fees Cost: $15/night $5 day-use (also RIDB 262603)", None),
 (6357, "https://blm.gov/press-release/fontenelle-creek-and-warren-bridge-campgrounds-open-summer", 10, 10, "designated campsite fees $10 per night (BLM 2023); Campendium May 2025 report $10", None),
 (6368, "https://www.blm.gov/press-release/blm-kemmerer-field-office-holds-cleanup-event-national-public-lands-day", 0, 0, "Slate Creek and Weeping Rock ... provide visitors with free camping (BLM 2022-09-07)", None),
 (6376, "https://www.blm.gov/visit/shirley-mountains", 0, 0, "... Prior Flat Campground ... Fees No Fee.", None),
 (9427, "https://developer.nps.gov/api/v1/campgrounds?parkCode=ciro", 14, 14, "City of Rocks Campground: Campsite Fee 14.00 (NPS campgrounds data)", "Plus a $10 reservation fee per booking."),
 (9775, "https://www.federalregister.gov/d/2026-04733", 20, 20, "a new $20 per site per night fee for overnight camping at Silver Creek and Wilson Lake campgrounds ... take effect on September 11, 2026", None),
 (9967, "https://www.blm.gov/visit/little-sahara-recreation-area", 18, 18, "requires a use fee, which includes access to campgrounds ... $18 per vehicle per night", "Recreation-area use fee, which covers camping; $120 annual pass."),
 (9969, "https://www.blm.gov/visit/little-sahara-recreation-area", 18, 18, "requires a use fee, which includes access to campgrounds ... $18 per vehicle per night", "Recreation-area use fee, which covers camping; $120 annual pass."),
 (12328, "https://www.blm.gov/visit/chimney-peak-recreation-area", 0, 0, "Chimney Peak Recreation Area (incl. Chimney Creek Campground) ... Fees No Fees", None),
 (12334, "https://www.blm.gov/visit/cottonwood-campground", 6, 6, "A $6.00 per campsite fee is required for camping at all BLM campsites (McCain Valley)", None),
 (12349, "https://www.blm.gov/visit/tk-jones-campground-and-boat-launch", 15, 15, "Fees $10 per day per vehicle for day-use; $15 per vehicle for overnight use; $75 annually", None),
 (12350, "https://www.blm.gov/visit/crossroads-campground", 5, 5, "Fees This is a first-come-first-serve campground. $5 per night.", None),
 (2308, "https://www.nps.gov/meve/planyourvisit/camping.htm", 38, 51, "Morefield ... $38.00 ... Full Hook-Up ... (Rate is based on two people ...) $51.00", "Standard $38; 15 full-hookup sites $51 for two people."),
 (6387, "https://www.nps.gov/grte/planyourvisit/colterbayrv.htm", 112, 117, "Pull-through ... $117.00; Back-In Sites (30ft RV or smaller) $112.00", "Back-in to 30 ft $112, pull-through $117; before taxes."),
]
F = []
for i, url, lo, hi, quote, note in ROWS:
    fees = {"nightly_low": lo, "nightly_high": hi}
    if hi: fees["currency"] = "USD"
    if note: fees["note"] = note
    F.append({"id": i, "fees": fees, "source": f"{url} ('{quote}', read 2026-10-16)"})
json.dump(F, open("loose_findings.json", "w"), indent=1, ensure_ascii=False)
print(len(F))
