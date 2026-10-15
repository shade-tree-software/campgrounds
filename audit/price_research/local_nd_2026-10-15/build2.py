"""ND local, second batch: RoverPass booking engine (claimed, bookable listings) and Hazen's webreserv page.
python3 -I build2.py > findings2.json"""
import json
ROWS = [
 (5958, 30, 30, "https://www.roverpass.com/c/medina-city-campground-medina-nd/booking/ (RoverPass booking API, audit/price_research/local_nd_2026-10-15/rp_nd.jsonl)",
  "RoverPass booking (City of Medina, request to book): 50-amp full-hookup sites $30 a night, tents $15, October 2026 and April and June 2027; RoverPass adds its own fees. Closed December through March."),
 (6041, 22, 22, "https://www.roverpass.com/c/dead-colt-creek-rec-area-lisbon-nd/booking/ (RoverPass booking API, audit/price_research/local_nd_2026-10-15/rp_nd.jsonl)",
  "RoverPass booking (Ransom County): 30/50-amp water and electric sites $22 a night for June 2027, tents $12-17; RoverPass adds a $5 platform fee and card processing. Closed October through spring."),
 (5895, 22, 30, "https://www.webreserv.com/hazenparksandrecreationnd (audit/price_research/local_nd_2026-10-15/nd_pages.jsonl)",
  "Hazen Parks and Recreation (webreserv): electric sites $22 a night, full hookups $30; cabins $55-120; $10 non-refundable deposit."),
]
out = []
for i, lo, hi, src, note in ROWS:
    out.append({"id": i, "fees": {"nightly_low": lo, "nightly_high": hi, "currency": "USD", "checked": "2026",
                "note": note + " Read 2026-10-15."}, "source": src + ", read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
