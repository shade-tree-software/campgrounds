"""Rutlader Outpost RV Park 2212 (KS), held from the Campspot pass of 2026-10-13 only for the Kansas hold, which AWH
lifted 2026-10-15: python3 -I rutlader_apply.py [--apply]. Campspot read through the driver (rutlader.jsonl)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

D = "2026-10-15"
SRC = ("https://www.campspot.com/park/rutlader-outpost-rv-park (Campspot API, park 987: 'Full Hookup Back In Site' $45 "
       "and 'Full Hookup Pull Through Site' $50 a night on every date read, 2026-10-17 to 2027-06-12, plus 'Online "
       "Booking Fee' $7.00; two back-in nights from 2026-10-20 $90 + $7 = $97, so the fee is per stay; no taxes "
       f"itemized; rutlader_2026-10-15/rutlader.jsonl), read {D}")


def main():
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path, encoding="utf-8"))
    e = next(r for r in rows if r["id"] == 2212)
    assert not e.get("fees")
    cs.apply_update(e, {"fees": {"nightly_low": 45, "nightly_high": 50, "currency": "USD", "reservation_fee": 7,
                                 "checked": "2026",
                                 "note": (f"Campspot's rates (read {D}): $45 a night for a full-hookup back-in site, "
                                          "$50 for a pull-through, the same October to June, plus a $7 online "
                                          "booking fee per stay.")},
                        cs.PROVENANCE: {"fees": {"source": SRC, "checked": D}}})
    e["inclusion_evidence"] += f"; re-check {D}: priced from Campspot, $45-50 a night (+$7 per stay)"
    cs.validate_row(e, "id 2212")
    print(json.dumps(e["fees"]))
    if "--apply" in sys.argv:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        print("written")


if __name__ == "__main__":
    main()
