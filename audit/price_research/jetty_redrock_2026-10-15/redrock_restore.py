"""Re-check of the two parks dropped 2026-10-11 under the login rule (AWH 2026-10-14 #3 softened it):
python3 -I redrock_restore.py [--apply].

- Jetty Park 13374 stays dropped: CampLife (1162) still quotes only its pavilions without a login, and Port
  Canaveral's own pages post no campsite rate (jetty_camplife.jsonl).
- Red Rock Park 13594 comes back: McKinley County now runs it and moved its booking to Rec1 on 2026-04-01, whose
  public catalog shows each site's 'Daily Rate (Flat Fee) ($27.99/Multi-Day)' and asks for an account only to add
  a site to the cart - a checkout login, which AWH's 2026-10-11 scope allows.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

D = "2026-10-15"
OLD = json.loads(subprocess.check_output(["git", "-C", ROOT, "show", "47a94840^:campgrounds.json"]))
CG = "https://www.co.mckinley.nm.us/437/Red-Rock-Campground"
REC1 = "https://secure.rec1.com/NM/mckinley-county-nm/"


def main():
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path, encoding="utf-8"))
    assert not any(r["id"] == 13594 for r in rows)
    e = next(r for r in OLD if r["id"] == 13594)
    e["website"] = f"{CG}\n{REC1}"
    e["note"] = ("McKinley County campgrounds in Red Rock Park, 6 mi east of Gallup under the red sandstone cliffs. Main "
                 "and West campgrounds: about 121 sites with water and 20/30/50-amp electric (no sewer), showers, "
                 "camp store, dump station. Reservations required, online or by phone; some sites are rented by the "
                 "month. Busy during the rodeo and the Red Rock Balloon Rally. --Claude")
    prov = e[cs.PROVENANCE]
    cs.apply_update(e, {
        "hookups": {"electric": 50, "water": True, "sewer": False},
        "fees": {"nightly_low": 27.99, "nightly_high": 27.99, "currency": "USD", "checked": "2026",
                 "note": f"Rec1's daily flat fee for a campsite (sites #002 and #068 read). Read {D}."},
        cs.PROVENANCE: dict(prov, hookups={"source": f"{CG} ('Q: AMP SERVICE? A: WE HAVE 20, 30, AND 50 AMP SERVICE'; "
                                                     f"'Q: DO YOU HAVE FULL HOOK-UPS? A: NO'), read {D}",
                                           "checked": D},
                            fees={"source": f"{REC1} catalog, Main Campground & Horse Stalls ('Daily Rate (Flat Fee) "
                                            f"($27.99/Multi-Day)'; 'An account is required to add reservations to "
                                            f"cart.'), read {D}", "checked": D}),
    })
    e["inclusion_evidence"] += (f"; re-check {D}: restored - McKinley County now runs the park and books on Rec1, "
                                "whose public catalog shows a $27.99 daily rate; an account is needed only to check "
                                "out (AWH 2026-10-11 scope), so the 2026-10-11 login drop no longer applies")
    cs.validate_row(e, "id 13594")
    rows.append(e)
    print(json.dumps({k: e[k] for k in ("website", "note", "hookups", "fees")}, indent=1))
    if "--apply" in sys.argv:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        with open(os.path.join(os.path.dirname(HERE), "dropped_2026-10-11.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"id": 13594, "name": e["name"], "state": "NM", "ownership": "local",
                                 "action": "restored", "why": "McKinley County's Rec1 catalog shows a $27.99 daily "
                                 "rate without a login; an account is needed only to check out"},
                                ensure_ascii=False) + "\n")
        print("written")


if __name__ == "__main__":
    main()
