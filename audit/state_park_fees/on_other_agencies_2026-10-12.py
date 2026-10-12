"""Ontario entries run by provincial agencies other than Ontario Parks: python3 -I on_other_agencies_2026-10-12.py [--apply]

The eight St. Lawrence Parks Commission campgrounds (Parks of the St. Lawrence) and Fort William Historical Park's RV
park are `ownership: provincial`, so they inherited the provincial:ON row - Ontario Parks' booking site, 5-month
window, 9 pm cutoff and 23-night maximum - none of which is theirs. They get policy_ref none (the rule for a campground
outside its province's park system), and the commission's campgrounds get its own booking channel: its site's
'Reservations' page sends every booking to reservations.parks.on.ca (a GoingToCamp host, slpc_booking_fees_*.json)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
SLPC = [8207, 8208, 8218, 8220, 8307, 12658, 12669, 12683]
FWHP = [8368]
cg_path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(cg_path, encoding="utf-8"))
by = {e["id"]: e for e in rows}
for i in SLPC + FWHP:
    e = by[i]
    assert e.get("ownership") == "provincial" and e.get("state") == "ON" and not e.get(cs.POLICY_REF), i
    e[cs.POLICY_REF] = cs.POLICY_REF_NONE
    if i in SLPC:
        prov = dict(e.get(cs.PROVENANCE) or {})
        prov["booking"] = {"source": "https://www.stlawrenceparks.com/reservations/ (bookings at reservations.parks.on.ca), read "
                                     f"{D}", "checked": D}
        cs.apply_update(e, {"booking": {"reservable": True, "platform": "goingtocamp",
                                        "url": "https://reservations.parks.on.ca/"}, cs.PROVENANCE: prov})
    cs.validate_row(e, label=e["name"])
    print(i, e["name"], e[cs.POLICY_REF], json.dumps(e.get("booking"), ensure_ascii=False))
if "--apply" in sys.argv:
    tmp = cg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, cg_path)
    print("written")
else:
    print("(dry run)")
