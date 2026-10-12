"""Mark the reservation minimums of New York's DEC campgrounds: python3 -I ny_dec_min_stay_2026-10-12.py [--apply]

AWH 2026-10-12: record DEC's per-campground minimums on each campground, as for the other minimum stays
(booking.min_stay + booking.note + provenance.booking + a dated MINIMUM STAY line on the note).

DEC's 2026 Summer Recreation Campground Summary (revised 1/12/26) gives each campground a 'RES MIN' of 1, 2 or 3 nights,
and its footnote says 'When the first campground opens for the season, the reservation minimums at all facilities will
become 1 night until closing' - Fish Creek and Wilmington Notch opened first, May 8 in 2026. So the minimum binds
bookings made before the season opens and never a booking made during it. 16 of our 43 DEC campgrounds list 2 nights
and Fish Creek Pond 3; the other 26 list 1 and get nothing. The booking site states no minimum on its pages (it does
confirm the 9-month window and same-day booking), so the summary is the source.

Each booking group's provenance becomes DEC's pages: the reservable/platform values some of these carried from note
prose are what DEC's reservations page says ('All reservations must be made using the ReserveAmerica system'), and
Ausable Point's 14-night maximum is its rules page's."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
SUMMARY = "https://dec.ny.gov/sites/default/files/2025-04/summerreccampgroundsummary.pdf"
RES = "https://dec.ny.gov/things-to-do/camping/reservations"
RULES = "https://dec.ny.gov/things-to-do/camping/campground-rules-regulations"
# entry id -> (name on DEC's summary, RES MIN nights)
MINIMUMS = {358: ("Fish Creek", 3), 20: ("Mongaup Pond", 2), 21: ("North/South Lake", 2),
            309: ("Lake George Battleground", 2), 345: ("Scaroon Manor", 2), 350: ("Nicks Lake", 2),
            1402: ("Woodland Valley", 2), 1403: ("Bear Spring Mountain", 2), 1422: ("Kenneth L. Wilson", 2),
            1423: ("Hearthstone Point", 2), 1424: ("Eagle Point", 2), 1426: ("Beaverkill", 2), 1429: ("Devil's Tombstone", 2),
            1430: ("Little Pond", 2), 1526: ("Ausable Point", 2), 13727: ("Rogers Rock", 2), 13728: ("Luzerne", 2)}
SEASON = "bookings made before DEC's season opens, May 8 in 2026"

cg_path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(cg_path, encoding="utf-8"))
by = {e["id"]: e for e in rows}
for i, (sname, n) in MINIMUMS.items():
    e = by[i]
    assert e.get("policy_ref") == "state:new-york-dec-campgrounds", i
    assert not (e.get("booking") or {}).get("min_stay") and "MINIMUM STAY" not in (e.get("note") or ""), i
    booking = {"min_stay": [{"nights": n, "applies": "always", "season": SEASON}],
               "note": (f"Reservations need at least {n} nights until DEC's season opens (May 8 in 2026, when its "
                        "first campgrounds open): 'When the first campground opens for the season, the reservation "
                        "minimums at all facilities will become 1 night until closing.' DEC's 2026 campground summary.")}
    sources = [f"{RES} ('All reservations must be made using the ReserveAmerica system')",
               f"{SUMMARY} (RES MIN {n} for '{sname}'; 'When the first campground opens for the season, the "
               "reservation minimums at all facilities will become 1 night until closing')"]
    if (e.get("booking") or {}).get("max_stay_nights") == 14:
        sources.insert(1, f"{RULES} ('Camping permits will not be issued for more than 14 nights')")
    prov = dict(e.get(cs.PROVENANCE) or {})
    prov["booking"] = {"source": " + ".join(sources) + ", read 2026-10-12", "checked": D}
    cs.apply_update(e, {"booking": booking, cs.PROVENANCE: prov})
    e["note"] = (e.get("note") or "").rstrip() + (
        f"  MINIMUM STAY: {n} nights on reservations made before DEC's season opens (May 8 in 2026); after that DEC "
        f"takes 1-night reservations at every campground (DEC 2026 campground summary, {D}). --Claude")
    cs.validate_row(e, label=e["name"])
    print(i, e["name"], json.dumps(e["booking"], ensure_ascii=False)[:160])
if "--apply" in sys.argv:
    tmp = cg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, cg_path)
    print("written")
else:
    print("(dry run)")
