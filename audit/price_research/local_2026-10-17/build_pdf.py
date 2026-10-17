#!/usr/bin/env python3
"""Findings from the fee-sheet PDFs the earlier local passes linked but never read (pdf_hits.jsonl, 2026-10-17)."""
import json, os
R = "read 2026-10-17"
rows = [
 (7253, 35, 45, "2025", "City of Kerrville FY25 fee sheet (effective 2024-10-01, still the one posted): water/electric hillside $35, 30A full hookup $40 hillside / $45 riverside, 50A full hookup riverside $45; tent sites $25; 4 people and 2 vehicles included.",
  "https://www.kerrvilletx.gov/DocumentCenter/View/44940/KSP-FY25-Fee-Sheet-effective-October-1-2024"),
 (9782, 35, 35, "2024", "City of Blackfoot RV park sheet (Sept 2024): 18 sites with 30/50A hookups, $35 a night, 14-night maximum.",
  "https://www.cityofblackfoot.org/DocumentCenter/View/1826/RV-Park-Information-092024-PDF"),
 (5651, 30, 30, "2026", "Renville County 2026 fee schedule: Lake Allie camping $30 a night (weekly $168); rustic sites $20.",
  "https://www.renvillecountymn.gov/vidoc/renville-county-fee-schedule/"),
 (5851, 27, 37.5, "2025", "Codington County 2025 brochure: electric $27 (20/30A) or $30 (with water), full hookup $32.50 (30A) or $37.50 (50A pull-through); tent $18; $5 online booking fee.",
  "https://codington.sdcounty.gov/wp-content/uploads/2025/01/6835-CampgroundBrochure25.pdf"),
 (11749, 75, 80, "2025", "Earl Warren Showgrounds RV rules (posted Oct 2025): $75 or $80 a night, credit card at booking.",
  "https://static1.squarespace.com/static/64bef16497737903eb151a68/t/690152d254c18377903ccea1/1761694418757/RV-RULES-REGULATIONS.pdf"),
 (4686, 35, 40, "2026", "Rome-Floyd Parks & Recreation site list (undated, linked from the current booking page): sites 1-31 with power and water, $35 a night, $38 on the river, one site $40; plus a $2 daily parking pass.",
  "https://www.rfpra.com/_files/ugd/367faf_2d0f8b17ebf74324b281c205ea32650b.pdf"),
 (6845, 25, 25, "2026", "City of Hobart sheet (undated, the one the city posts): 50A hookups $25 a day, $150 a week, $500 a month.",
  "https://hobartok.gov/documents/390/lions_RV.pdf"),
 (12525, 20, 20, "2025", "Shawville Resolution #107-25 (July 2025): trailers and RVs $20 a day; $100 a week after the first two weeks.",
  "https://shawville.ca/wp-content/uploads/2025/07/Policy-Mill-Dam-Park-Event-Use.pdf", "CAD"),
 (10504, 28, 35, "2023", "City of Oroville 2023 fee sheet (still the one posted): May 1-Oct 14 standard $28, utility $35, primitive $18; off season $19/$26/$12; $8 reservation fee.",
  "https://oroville-wa.com/wp-content/uploads/2023_park_fees__policies_.pdf"),
 (2198, 25, 35, "2024", "Clay County 2024 rates: 30A $25 a night, 50A $30, sewer hookup $35; tent $10.",
  "https://www.claycountykansas.org/DocumentCenter/View/1721/Clay-County-Park-Fees-and-Rates-2024"),
 (3916, 45, 46, "2026", "Harbor Beach 2026 camping fees: RV under 30 ft $45, over 30 ft $46 ($50/$51 holidays); pop-up or tent $36, rustic $29; $8 reservation fee.",
  "https://static1.squarespace.com/static/5e66754612f5c46afd957255/t/692dbe1893cd2926bb21a51f/1764605464095/North+Park+Rates+2026.pdf"),
 (3932, 33, 43, "2026", "Jackson County 2026 camping fees: modern 30A $33 county resident / $38 non-resident, 50A $38 / $43; rustic $25 / $30; 10-night maximum.",
  "https://www.co.jackson.mi.us/DocumentCenter/View/22677/Camping-Fees-2026-Season?bidId="),
 (3937, 33, 43, "2026", "Jackson County 2026 camping fees: modern 30A $33 county resident / $38 non-resident, 50A $38 / $43; 10-night maximum.",
  "https://www.mijackson.org/DocumentCenter/View/22677/Camping-Fees-2026-Season?bidId="),
 (4018, 20, 30, "2024", "St. James Township campground sheet (Nov 2024): non-electric sites $20 a day, electric $30.",
  "https://webgen1files1.revize.com/stjamestwpmi/Campground%20WEBSITE%20Update%2011-1-24.pdf"),
 (2161, 20, 25, "2026", "Winfield comprehensive fee schedule (Jan 2026), City Lake: electric hookup $20 a day, electric/water/sewer $25 (recreational license included); primitive $10.",
  "https://cms2.revize.com/revize/winfield/Comprehensive%20Fee%20Schedule%20eff%20Jan%202026.pdf?t=202512311030240"),
 (2201, 17, 17, "2026", "Winfield comprehensive fee schedule (Jan 2026), Fairgrounds: all camping $17 per 24 hours ($5 primitive with a special-event contract).",
  "https://cms2.revize.com/revize/winfield/Comprehensive%20Fee%20Schedule%20eff%20Jan%202026.pdf?t=202512311030240"),
 (7244, 15, 18, "2023", "City of Yoakum manual of fees (adopted 2022, last revised Sept 2023, still the one posted): 30A with utilities $15 a night, 50A $18 (seniors $13/$15); no utilities $8.",
  "https://cms5.revize.com/revize/yoakum/Manual%20of%20Fees%20and%20Service%20Charges%202023.pdf"),
]
out = []
for r in rows:
    i, lo, hi, yr, note, url = r[:6]
    out.append({"id": i, "fees": {"nightly_low": lo, "nightly_high": hi, "currency": r[6] if len(r) > 6 else "USD",
                "checked": yr, "note": note + " Read 2026-10-17."}, "source": f"{url} (audit/price_research/local_2026-10-17/pdf_hits.jsonl), {R}"})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings_pdf.json"), "w"), indent=1, ensure_ascii=False)
print(len(out))
