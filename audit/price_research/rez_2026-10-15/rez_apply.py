"""The two Rez (Pearl River Valley Water Supply District) campgrounds left out of the CampLife pass:
python3 -I rez_apply.py [--apply]. Rates from the Rez's own pages (read 2026-10-15); CampLife's quotes
(rez_camplife.jsonl) match (nights x rate + $5) x 1.032 on every site type, as on Goshen Springs and Leake County.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

D = "2026-10-15"
REZ = "https://www.therez.ms.gov/parks-recreation/camping/"
TL_CL = "https://www.camplife.com/campground/Timberlake+Campground"      # the Timberlake page's own button
CB_CL = "https://www.camplife.com/1225/reservation/step1"                # Coal Bluff's button, minus its 2023 dates
DO = {
    5123: dict(
        web=TL_CL,
        note=("Large public campground on Ross Barnett Reservoir run by the Pearl River Valley Water Supply District "
              "(The Rez); ~272 sites, concrete pull-through and back-in pads, full hookups, pool, boat launch, disc "
              "golf, laundry. Nightly sites reservable online (CampLife); 30-day sites have a waiting list. --Claude"),
        fees={"nightly_low": 40, "nightly_high": 45, "currency": "USD", "reservation_fee": 5, "checked": "2026",
              "note": (f"From the Rez's Timberlake page (read {D}): $40 a night for a full-service RV site, $45 for a "
                       "premium, waterfront or pull-through site; pop-up sites with water and electric $35. Each stay "
                       "also carries a flat $5, and CampLife adds 3.2% to the whole quote: one night is $46.44 at $40 "
                       "and $51.60 at $45. 30-day sites ($660-710) have only a waiting list.")},
        src=(f"{REZ}timberlake ('Reserved: $40'; 'Reserved Premium: $45'; 'Pull-Thru: $45'; 'Pop Up Water & "
             f"Electricity: $35'; 'RV Full Service (Regular): $40'; '30-Day Standard Plus (currently no vacancy; "
             f"waiting list only)'), read {D}; https://www.camplife.com/1223/reservation/step1 (one night from "
             f"2026-10-17: Back In Nightly $46.44, Back In Nightly Waterfront $51.60, Pop Up W/E Nightly $41.28, "
             f"Pull Thru Nightly $51.60; two nights from 2026-10-20 Waterfront $98.04: (nights x rate + $5) x 1.032; "
             f"rez_2026-10-15/rez_camplife.jsonl), read {D}"),
        ie=f"re-check {D}: priced from the Rez's Timberlake page, $40-45 a night (CampLife quotes agree)"),
    13442: dict(
        web=CB_CL,
        fees={"nightly_low": 30, "nightly_high": 30, "currency": "USD", "reservation_fee": 5, "checked": "2026",
              "note": (f"From the Rez's Coal Bluff page (read {D}): $30 a night for a full-service RV site; 30-day "
                       "sites $450. Each stay also carries a flat $5, and CampLife adds 3.2% to the whole quote: one "
                       "night is $36.12, two $67.08. Online reservations required.")},
        src=(f"{REZ}coal-bluff ('Nightly RV Full Service: $30'; '30-Day Standard Plus Interior: $450'; 'You must make "
             f"reservations before choosing your site.'), read {D}; {CB_CL} (Back In Nightly one night from "
             f"2026-10-17 $36.12, two from 2026-10-20 $67.08: (nights x $30 + $5) x 1.032; "
             f"rez_2026-10-15/rez_camplife.jsonl), read {D}"),
        ie=f"re-check {D}: Rez $5 per-stay fee added and CampLife linked; $30 confirmed on the Rez page"),
}


def main():
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path, encoding="utf-8"))
    for e in rows:
        v = DO.get(e["id"])
        if not v:
            continue
        links = e["website"].split("\n")
        if v["web"] not in links:
            e["website"] = "\n".join(links + [v["web"]])
        if v.get("note"):
            e["note"] = v["note"]
        prov = dict(e.get(cs.PROVENANCE) or {})
        assert (prov.get("fees") or {}).get("method") not in ("manual", "reported")
        prov["fees"] = {"source": v["src"], "checked": D}
        cs.apply_update(e, {"fees": v["fees"], cs.PROVENANCE: {"fees": prov["fees"]}})
        ie = e.get("inclusion_evidence") or ""
        e["inclusion_evidence"] = f"{ie}; {v['ie']}" if ie else v["ie"]
        cs.validate_row(e, f"id {e['id']}")
        print(e["id"], e["name"], json.dumps(e["fees"])[:120], "|", e["website"].replace("\n", " ; "))
    if "--apply" in sys.argv:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        print("written")


if __name__ == "__main__":
    main()
