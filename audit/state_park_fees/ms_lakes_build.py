"""MS state fishing lakes: MDWFP's permit fees (Title 40 Part 3 Rule 2.1, rate sheet effective 2023-06-23,
the rule as posted on mdwfp.com rev. 04/2023), read 2026-10-12.

    python3 -I ms_lakes_build.py OUT

Daily camping (24 hours) $22, $25 at Calling Panther Lake; primitive/tent camping without electricity $17;
62+ and disabled $15; no reservations. Each lake's page says how many developed sites (electric and water)
it has and whether it has primitive camping."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
RULE = ("https://www.mdwfp.com/sites/default/files/2024-04/40-miss-admin-code-part-3-rule-21-state-fishing-lakes-rules-"
        "and-regulations-rev-04-2023-final.pdf")
# id: (lake page slug, developed sites, has primitive camping, extra)
L = {4999: ("calling-panther-lake", "21 sites (and 2 accessible ones) with electric, water and sewer", False, ""),
     5008: ("lake-claude-bennett", "31 sites with electric and water", False, ""),
     5009: ("lake-columbia", "6 sites with electric and water", True, ""),
     5010: ("lake-jeff-davis", "13 sites with electric and water", True, ""),
     5011: ("lake-lamar-bruce", "11 sites with electric and water", True, ""),
     5014: ("lake-mary-crawford", "20 sites with electric and water", True, ""),
     5015: ("lake-mike-conner", "15 sites with electric and water", True, ""),
     5016: ("lake-monroe", "12 sites with electric and water", False,
            " The lake's page says camping is currently not available and the campground is closed until further notice."),
     5017: ("lake-perry", "15 sites with electric and water", True, ""),
     5018: ("prentiss-walker-lake", "18 sites with electric and water", True, ""),
     5019: ("lake-tom-bailey", "22 sites with electric and water", True, ""),
     5026: ("tippah-county-lake", "22 sites with electric and water", True, ""),
     5075: ("simpson-county-lake", "11 sites with electric and water", True, "")}
out = []
for eid, (slug, dev, prim, extra) in sorted(L.items()):
    day = 25 if eid == 4999 else 22
    if prim:
        fees = {"nightly_low": 17, "nightly_high": 17, "currency": "USD", "surcharges": {"electric": day - 17}}
        text = f"${day} a night for one of the {dev}; primitive camping without electricity $17."
    else:
        fees = {"nightly_low": day, "nightly_high": day, "currency": "USD"}
        text = f"${day} a night ({dev})."
    fees["checked"] = "2026"
    fees["note"] = (text + " Campers 62 and older and disabled campers $15. First come, first served: no reservations; "
                    "the daily camping permit includes fishing and boat launching for up to 8 people." + extra +
                    f" MDWFP's state fishing lake fees (rate sheet effective 2023-06-23), read {D}.")
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees,
                "source": f"{RULE} (E. Camping ... Permits: daily camping $22, Calling Panther Lake $25, primitive $17, read {D}) "
                          f"+ https://www.mdwfp.com/fishing-boating/lakes/{slug} (the lake's campground, read {D})"})
json.dump(out, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)
print(len(out), 'MS lake findings')
