"""Claybanks Township Park 3960 (MI): python3 -I claybanks_apply.py [--apply]. The township's camping page (read
2026-10-15) posts the rates, the weekend/holiday minimums and its Campspot link, which the entry lacked."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

D = "2026-10-15"
PAGE = "https://www.claybankstownship.org/claybanks-township-park/camping-at-claybanks-township-park/"
CS = "https://www.campspot.com/book/claybanks-township-park"
SRC = (f"{PAGE} ('Campsite (with electric): $40/day'; 'Campsite on Holiday Weekend (with electric): $50/day'; "
       "'Weekend reservations must be for full weekend (2 days)'; 'Holiday weekend reservations must be for full "
       f"holiday weekend (3 days)'; 'All cancellations are subject to a $25 cancellation fee'), read {D}")


def main():
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path, encoding="utf-8"))
    e = next(r for r in rows if r["id"] == 3960)
    assert not e.get("fees")
    e["website"] = e["website"].replace("https://www.campspot.com", CS) if CS not in e["website"] else e["website"]
    assert e["website"].split("\n") == [PAGE, CS], e["website"]
    e["note"] = ("Oceana County township park on a Lake Michigan bluff. 68 sites (42 electric, 26 primitive), grassy "
                 "lots with fire pit & picnic table; stairs/paths down to beach. Open May 1-Sept 18; reservable "
                 "online (Campspot). Operated by Claybanks Township. Alcohol-free. Minimum stay (read 2026-10-15): "
                 "a full weekend (2 nights), 3 nights on holiday weekends. --Claude")
    prov = e[cs.PROVENANCE]
    cs.apply_update(e, {
        "fees": {"nightly_low": 40, "nightly_high": 50, "currency": "USD", "checked": "2026",
                 "note": (f"The township's posted rates (read {D}): $40 a day for a site with electric, $50 on a "
                          "holiday weekend. Cancellation costs $25.")},
        "booking": {"reservable": True, "platform": "campspot",
                    "min_stay": [{"nights": 2, "applies": "weekend"}, {"nights": 3, "applies": "holiday"}]},
        cs.PROVENANCE: {"fees": {"source": SRC, "checked": D},
                        "booking": {"source": f"{SRC}; kept from the note: reservable on Campspot", "checked": D}},
    })
    e["inclusion_evidence"] += (f"; re-check {D}: priced from the township's camping page, $40-50 a night; its "
                                "Campspot listing found there (2-night weekend minimum, marked)")
    cs.validate_row(e, "id 3960")
    print(json.dumps({k: e[k] for k in ("website", "fees", "booking")}, indent=1)[:900])
    if "--apply" in sys.argv:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        print("written")


if __name__ == "__main__":
    main()
