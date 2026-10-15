"""Second findings batch (rest.jsonl, read 2026-10-15): park camping-activity pages on mycountyparks.com and
county conservation sites. python3 -I build2.py > findings2.json"""
import json
M = "https://www.mycountyparks.com"
ROWS = [
 (2985, 20, 25, M + "/county/plymouth/park/hillview-recreation-area/Activity/Camping",
  "Plymouth County: Deer Ridge $25 a day, Bur Oak and Beaver Creek $20 ($150 / $120 a week paid in full on arrival). Open May 1 - October 14."),
 (2997, 20, 20, M + "/county/Adair/Park/Mormon-Trail-Park/Activity/Camping",
  "Adair County: camper sites $20; tent $15, $20 with electric. The page dates these fees July 21, 2021."),
 (3001, 15, 15, "https://www.pagecountyconservation.com/pierce-recreation-area",
  "Page County: electric and water sites $15 a night, primitive $6; first come, first served."),
 (3022, 25, 25, M + "/county/Emmet/Park/Wolden-Recreation-Area-Campground/Activity/Camping",
  "Emmet County: electric sites $25 a night, non-electric $15. Mid-April to mid-October."),
 (3061, 17, 17, M + "/county/madison/park/pammel-state-park/Activity/Camping",
  "Madison County: 30/50-amp electric and water pads $17 a night, tent $10; $5 reservation fee per site (515-462-3536).", 5),
 (3076, 25, 25, M + "/county/Emmet/Park/Tuttle-Lake-Recreation-Area-Campground/Activity/Camping",
  "Emmet County: electric $25 a night, non-electric $15. Mid-April to mid-October."),
 (3133, 15, 15, "https://www.fayettecountyconservation.org/twin-bridges-park",
  "Fayette County: $15 a night with electricity, $10 without."),
 (3143, 15, 15, "https://www.claytoncountyconservation.org/bloody-run-park",
  "Clayton County: primitive (rough) camping only, $15 a night; reservable online or first come, first served."),
 (3162, 20, 20, "https://www.buchanancounty.iowa.gov/services/conservation/jakway_campground.php",
  "Buchanan County: $20 a night with electricity, $15 without."),
 (3190, 25, 30, M + "/county/black-hawk/park/black-hawk-park/Activity/Camping",
  "Black Hawk County: electric $25 a night, full hookup $30, non-electric $18; 'fees subject to change'."),
]
out = []
for row in ROWS:
    i, lo, hi, src, note = row[:5]
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if len(row) > 5:
        fees["reservation_fee"] = row[5]
    fees.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": fees, "source": src + " (Fees text; audit/price_research/local_mycountyparks_2026-10-15/rest.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
