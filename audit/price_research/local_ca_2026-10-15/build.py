"""CA local findings from ca_pages.jsonl + peeks (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV sites (electric/hookup where sold); tent/primitive in the note."""
import json
HUM = "https://humboldtgov.org/1429/Parks-Trails"
HUMN = "Humboldt County Parks: camping $30 a night per site, cash or check only, first come, first served."
SLO = "https://slocountyparks.com/fee-schedule/"
SLON = "SLO County Parks fee schedule: full hookup $56-65 (weekday off-season to holiday), electric-only $48-57 (Memorial Day-Labor Day only), primitive $38-49; $12 reservation fee per site; 3% card fee."
SB = "San Bernardino County Regional Parks: with hookup $45 Mon-Thu, $55 Fri-Sun; without hookup $35/$45; $10 non-refundable reservation fee; 14 days in 30."
ROWS = [
 (11620, 45, 45, None, "https://parks.lacounty.gov/castaic-lake-state-recreation-area-2/", "LA County Parks: RV camping $45 a site a day, tent $23; vehicle entry $15 a day."),
 (11716, 30, 30, None, HUM, HUMN),
 (11718, 55, 60, None, "https://avfair.com/rv-park/", "Antelope Valley Fair RV park: 30-amp $55 a day, 50-amp $60; weekly and monthly rates; first come, first served."),
 (11723, 62.15, 62.15, None, "https://www.fresnofair.com/p/other/rv-parking", "Fresno Fair: full hookups $62.15 a night, all fees included; stays up to 20 days; no RV rentals Sep 1 - Oct 31."),
 (11724, 30, 30, None, HUM, HUMN),
 (11730, 40, 40, None, "https://www.frogtown.org/rv-park", "Frogtown RV Park: $40 a night with water, power and sewer ($35 seniors), tents $25; self-service pull-throughs."),
 (11731, 40, 55, 10, "https://parks.sbcounty.gov/park/calico-ghost-town-regional-park/", "San Bernardino County: partial hookup $40 weekday / $50 weekend, full hookup $45 / $55, no hookup $35 / $45; $10 reservation fee; per-person admission applies."),
 (11736, 30, 30, None, HUM, HUMN + " Three-night maximum."),
 (11737, 61, 70, 12, SLO, "SLO County Parks fee schedule: Coastal Dunes full hookup $61-70 (weekday off-season to holiday); $12 reservation fee per site; 3% card fee."),
 (11750, 48, 65, 12, SLO, SLON),
 (11771, 24, 24, None, "https://mtrp.org/reservations/", "Mission Trails Regional Park: $24 a night, Friday and Saturday nights only."),
 (11783, 48, 65, 12, SLO, SLON),
 (11786, 55, 55, None, "https://www.mariposafair.com/camping", "Mariposa County Fair: RV $55 a night per rig, tents $35; first come, first served."),
 (11790, 45, 55, 10, "https://parks.sbcounty.gov/park/mojave-narrows-regional-park/", SB),
 (11791, 45, 55, 10, "https://parks.sbcounty.gov/park/mojave-river-forks-regional-park/", SB),
 (11793, 85, 85, None, "https://montereycountyfair.com/monterey-rv-park/", "Monterey County Fair RV park 2026: $85 a night, $510 a week; 2027 $88; discounts for military, veterans and seniors."),
 (11794, 40, 60, None, "https://motherlodefair.org/facilities/rv-camping/", "Mother Lode Fair: 30-amp $40 a day, 50-amp $60; 10% off the daily rate with Good Sam, AAA or AARP; first come, first served."),
 (11796, 45, 65, None, "https://www.nevadacountyfair.com/p/visit-our-rv-park1/visit-our-rv-park", "Nevada County Fair RV park: water and electric $45 a night, full hookup $55, premium $65; no tents."),
 (11798, 45, 45, None, "https://ocfair.com/venue-rentals/area-lodging-on-site-camping/", "OC Fair: $45 a night with 20-amp electric, water and sewer; first come, first served."),
 (11804, 155, 155, 13, "https://www.portsanluis.com/2163/RV-Camping", "Port San Luis: full hookup $155 a night, trailer-boat dry camping $122; $13 reservation fee."),
 (11809, 45, 45, None, "https://www.redwoodacres.com/rv-park.html", "Redwood Acres: $45 a night, RVs only; Escapees $38."),
 (11810, 40, 40, None, "https://www.redwoodempirefair.com/rv-park-local-attractions", "Redwood Empire Fair: standard $40 a night, Good Sam $37, no hookups $35."),
 (11820, 70, 95, None, "https://sonomacountyfair.com/pages/rvpark", "Sonoma County Fair from June 1, 2026: 30-amp $70 a night, 50-amp $75, pull-through $90-95; no tents."),
 (11833, 40, 40, None, "https://tricountyfair.com/camping-2/", "Tri-County Fair: $40 a night for all RVs, $215 for 6 nights."),
 (11835, 30, 40, None, "https://www.tbvfair.com/p/other/year-round-rv-park", "Tulelake-Butte Valley Fair: partial hookup $30 a day, full hookup $40; Passport America $20."),
 (11843, 60, 60, None, "https://www.stancountyparks.com/woodward-reservoir", "Stanislaus County: RV/trailer hookup site $60 a night ($55 resident), general $50, basic $40; vehicle day use $20."),
 (11844, 50, 50, None, "https://www.yolocountyfair.net/p/rv-park", "Yolo County Fair: $50 a night, $300 a week, full hookups."),
 (11845, 45, 55, 10, "https://parks.sbcounty.gov/park/yucaipa-regional-park/", SB),
 (11819, 48, 65, 12, SLO, SLON),
 (11838, 30, 30, None, HUM, HUMN),
 (12192, 30, 30, None, "https://www.tcpud.org/parks-facilities/facilities-parks-and-rentals/lake-forest-campground", "Tahoe City PUD: $30 a night, 10 consecutive days; no hookups, showers or dump; first come, first served."),
 (12380, 32, 56, None, "https://explorelakepiru.com/camping/", "Lake Piru: electric $32 off-season / $43 peak, full hookup $45 / $56, basic $28 / $36; peak April-September."),
 (12388, 35, 45, 3.5, "https://www.tvrpd.org/brite-lake", "Tehachapi Valley Rec: water and electric $35 a night, full hookup $45, tents $30; $3.50 transaction fee."),
 (12404, 48, 48, None, "https://boladoparkeventcenter.com/rv-camping/", "Bolado Park: $48 a night."),
 (12436, 57, 75, 12, "https://www.nidwater.com/peninsula-campground", "Nevada Irrigation District 2026: wooded sites $57 and $68, lakefront $75; $12 reservation fee."),
]
out = []
for i, lo, hi, rf, src, note in ROWS:
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": src + " (audit/price_research/local_ca_2026-10-15/ca_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
