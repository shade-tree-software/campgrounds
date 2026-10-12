"""DE findings: the booking site's per-site prices, read 2026-10-12 (de_booking_sample_2026-10-12.jsonl).

    python3 -I de_build.py OUT

Delaware's 2026 rate schedule (destateparks.com/wp-content/uploads/2026/02/business_2026_Rates_and_Fees.pdf)
prices by season (winter / spring-fall / summer) and weekday / weekend, but the site refuses every
fetch path (CloudFront 403, also to WebFetch), so the booking site's own prices are the source:
sites sampled across each park for Tue 2027-01-12, Tue 2027-04-13, Tue 2027-07-13 and Sat 2027-07-17.
The base range runs from the winter weekday to the summer weekday price of the park's plain RV site.
Non-residents pay the resident price x 1.25, rounded up to the dollar, at every sampled site except
Cape Henlopen's higher-priced sites; the reservation fee is $4."""
import json, os, sys
out_path = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
# id: (parkId, low, high, weekend, surcharges, sentence)
P = {
    215: (360118, 23, 33, 5, {}, "Every site has water and electric (50 amp): $23 a night on a winter weekday, $27 in "
         "spring and fall, $33 in summer, $38 on a summer Saturday."),
    649: (360119, 32, 46, 5, {}, "Every RV site has full hookups (50 amp): $32 a night on a winter weekday, $40 in spring "
         "and fall, $46 in summer, $51 on a summer Saturday."),
    670: (360108, 35, 53, 3, {"premium_site": 10}, "Every RV site has water and electric (50 amp): $35 a night on a "
         "winter weekday, $42 in spring and fall, $53 in summer, $56 on a summer Saturday; some sites in loops D and E "
         "are $10 more ($63 on a summer weekday; non-residents pay about 1.2 times these)."),
    867: (360122, 23, 33, 5, {}, "Every site has water and electric (30 or 50 amp): $23 a night on a winter weekday, $27 "
         "in spring and fall, $33 in summer, $38 on a summer Saturday."),
    868: (360109, 25, 43, 3, {"full_hookup": 14}, "$25 a night for a site without hookups on a winter weekday, $32 in "
         "spring and fall, $43 in summer, $46 on a summer Saturday; full hookups (50 amp) $32 / $47 / $57 / $60."),
}
out = []
for eid, (pid, low, high, wk, s, text) in sorted(P.items()):
    surch = dict(s)
    surch["weekend"] = wk
    fees = {"nightly_low": low, "nightly_high": high, "currency": "USD", "reservation_fee": 4,
            "nonresident": {"type": "multiplier", "factor": 1.25}, "surcharges": surch, "checked": "2026",
            "note": text + (f" Non-residents pay 1.25 times the resident price, rounded up. $4 reservation fee. The "
                            f"booking site's prices for 2027 nights, read {D} (Delaware's 2026 rate schedule PDF "
                            f"refuses every fetch).")}
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees,
                "source": f"delawarestateparks.reserveamerica.com parkId {pid} (sampled sites' resident and "
                          f"non-resident prices for 2027-01-12, 2027-04-13, 2027-07-13 and 2027-07-17, read {D})"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'DE findings')
