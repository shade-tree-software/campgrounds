"""SK local findings from sk_pages.jsonl (operators' own pages, read 2026-10-15), CAD. python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/non-serviced in the note. Source = first page whose rate lines contain KEY,
or the URL given when KEY starts with http (a peek at the same page, 2026-10-15)."""
import json
ROWS = [
 (9162, 35, 50, None, "Daily Camping Rates", "Brightsand Lake Regional Park 2026: 15-amp $35 a night, 30-amp $40, with water $45, with water and sewer $50 (plus GST/PST); non-serviced $30; park entry $10 a day."),
 (9211, 25, 25, None, "$25 per night (30 amp sites)", "Town of Canora: 30-amp sites $25 a night; no reservations."),
 (9217, 30, 30, None, "Electrical site $30", "Town of Churchbridge 2026: electric sites $30 a night, non-electric $20."),
 (9223, 40, 40, None, "-$40.00 per night", "RM of Craik (Aylesbury): $40 a night; book by phone."),
 (9229, 30, 35, None, "30 amp – $30/night", "Town of Foam Lake: 30-amp $30 a night, 50-amp $35, tents $18."),
 (9232, 43, 53, None, "RV Sites 15 amp 30 amp 50 amp", "City of Saskatoon 2026: RV sites $43 (15-amp), $48 (30-amp), $53 (50-amp) a day; tents $28."),
 (9233, 30, 30, None, "Full Service : $30", "Town of Gravelbourg: full service $30 a night, non-serviced $20."),
 (9238, 24, 35, None, "Electric, Sewer & Water Site | Per Night", "Kindersley Regional Park: full service $35 a night, electric $30, 15-amp $24."),
 (9249, 44, 44, None, "NIGHTLY $44.00", "Town of Lumsden 2026: serviced sites with electricity and water $44 a night, non-serviced $27."),
 (9256, 30.80, 30.80, None, "Electric/Day", "City of Melfort: electric $30.80 a day including taxes, non-electric $25.30."),
 (9259, 35, 35, None, "$35 for sites with electrical", "Town of Milestone: electric sites $35 a night, non-electric $20; first come, first served."),
 (9263, 20, 20, None, "30 Amp. Plug-in", "Town of Nokomis: 15- or 30-amp sites $20 a day, non-electric $10."),
 (9266, 28, 40, None, "Full Service: $40.00/night", "Oungre Memorial Regional Park: full service $40 a night, 30-amp $33, 15-amp $28, tents $25."),
 (9267, 35, 35, None, "Camping Price | Daily | $35.00", "Outlook & District Regional Park: $35 a day; vehicle pass $8 a day."),
 (9268, 43, 50, None, "https://www.palliserregionalpark.com/rates-reservations/rates/", "Palliser Regional Park (2025 rates): water/electric $43 a day, full hookup $48, 50-amp full hookup $50, non-serviced $30; park entry $15 a day not included."),
 (9272, 35, 35, None, "Camping Fees are $35/night", "City of Weyburn: power and water sites $35 a night, non-serviced $20."),
 (9278, 35, 35, None, "Sites #1-8 are $35.00", "Town of Cut Knife: 30-amp with water $35 a night; first come, first served."),
 (9283, 50, 58, None, "15/30 Amp | $50.00", "City of Lloydminster: 15/30-amp $50 a day, 50-amp $58, including GST."),
 (9285, 36, 44, None, "https://townofwhitewood.ca/whitewood-campground", "Town of Whitewood: full service 50-amp $44 a night, 50-amp with water $36."),
]
pages = [json.loads(l) for l in open("sk_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    if key.startswith("http"):
        urls = [key]
    else:
        urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_sk_2026-10-15/sk_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
