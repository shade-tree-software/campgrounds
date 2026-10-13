"""Nevada State Parks findings, read 2026-10-12 (texts in nv_fee_pages_2026-10-12.txt).

    python3 -I nv_build.py OUT

Nevada State Parks' fees page (parks.nv.gov/fees, the same lines on each park's page) gives each park's camping fee
'per vehicle, per night': $15.00 (Non-NV Vehicles: $20.00) at most parks, $20.00 ($25.00) at Big Bend of the Colorado
and Valley of Fire, '+ $10.00 for sites with utility hook ups' where a park has them. The reservations page: 'Visitors
pay a non-refundable $5.00 transaction fee per reservation', bookable 3 days to 11 months ahead on ReserveNevada (US
eDirect, API nevadardr.usedirect.com/NevadaRDR/rdr/). The booking site lists each park's campgrounds and site types
(nv_places_2026-10-12.json, rdr_place.py), which say which campgrounds have hookup sites; its per-site rate is a flat
$10.00 at every campsite of every park, hookups or not (nv_booking_rates_2026-11_2026-10-12.jsonl, rdr_rates.py), the
site part of the per-vehicle fee, so the fee table is the price. Each entry: base = the park's fee for a site without
hookups where a 23-ft rig can use one, else for a hookup site; +$10 where its campground has hookup sites; non-Nevada
vehicles +$5 a night; reservation fee $5; weekend 0 (one fee every night). No entrance is recorded: the camping fee is
charged per vehicle."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
FEES = "https://parks.nv.gov/fees"
RES = "https://parks.nv.gov/about/reservations"
NR = {"type": "surcharge", "amount": 5, "per": "night", "applies_to": "base"}
# entry -> (park page slug, PlaceId, fee, hookups: none / some / all, what the booking site lists)
ENTRY = {
    11191: ("berlin-ichthyosaur", 2, 15, "none", "Loop 1: sites without hookups"),
    11192: ("beaver-dam", 1, 15, "none", "Campgrounds A and B: sites without hookups (the park: parking for 'one vehicle and a "
                                         "small trailer'; first come, first served from November 1)"),
    11193: ("kershaw-ryan", 12, 15, "all", "Loop 1: water and electric sites (the primitive area is tent only)"),
    11194: ("dayton", 7, 15, "none", "Loop 1: sites without hookups"),
    11195: ("cave-lake", 5, 15, "none", "Lake View: sites without hookups"),
    11196: ("wild-horse", 27, 15, "some", "Loop 1: sites without hookups; Loop 2: water and electric"),
    11197: ("cave-lake", 5, 15, "none", "Elk Flat: sites without hookups"),
    11198: ("ward-charcoal-ovens", 25, 15, "none", "Willow Creek: sites without hookups"),
    11199: ("lahontan", 13, 15, "none", "Developed 7, 9th Street, River Camp and the dispersed beach areas: no hookups"),
    11200: ("big-bend-of-the-colorado", 3, 20, "some", "Loop 1: water, electric and sewer; a primitive area without"),
    11201: ("rye-patch", 16, 15, "some", "Lower and Upper campgrounds: sites without hookups and 3 electric sites"),
    11203: ("washoe-lake", 26, 15, "some", "Loop A: water and electric; Loop B: sites without hookups"),
    11204: ("valley-of-fire", 22, 20, "none", "Arch Rock: sites without hookups"),
    11205: ("valley-of-fire", 22, 20, "some", "Atlatl Rock: sites without hookups, water and electric, and electric"),
    11206: ("cathedral-gorge", 4, 15, "all", "Loop 1: electric sites (the tent-only sites are 22 ft)"),
    11207: ("echo-canyon", 8, 15, "all", "RV Campground: water, electric and sewer sites"),
    11208: ("spring-valley", 21, 15, "some", "Horsethief Gulch: the lower loop's electric sites and the upper loop without"),
    11209: ("fort-churchill", 10, 15, "none", "Samuel Buckland: sites without hookups"),
    11210: ("lahontan", 13, 15, "none", "Silver Springs Beach (Developed 7): sites without hookups"),
    11211: ("south-fork", 18, 15, "some", "East Campground: electric (some water and sewer) sites; Southwest Shores without"),
    11212: ("walker-river", 24, 15, "some", "River Bend: sites without hookups; Quail Run: water and electric"),
}
out = []
for eid, (slug, pid, fee, hook, what) in sorted(ENTRY.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    base = fee + (10 if hook == "all" else 0)
    sur = {"weekend": 0}
    if hook == "some":
        sur["electric"] = 10
    text = (f"${fee} per vehicle a night for Nevada vehicles, ${fee + 5} for others" +
            (", plus $10 at a site with utility hookups" if hook != "none" else "") +
            (" (every RV site here has them)" if hook == "all" else "") +
            ". Plus the $5 reservation transaction fee. " + f"On the booking site: {what}. "
            f"Nevada State Parks' fees and reservations pages and ReserveNevada, read {D}.")
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": base, "nightly_high": base, "currency": "USD", "nonresident": NR, "reservation_fee": 5,
        "surcharges": sur, "checked": "2026", "note": text},
        "source": f"{FEES} ({slug}: 'Camping: ${fee}.00 per vehicle, per night (Non-NV Vehicles: ${fee + 5}.00 ...)'"
                  + (" '+ $10.00 for sites with utility hook ups'" if hook != "none" else "") +
                  f") + {RES} ($5.00 transaction fee per reservation) + reservenevada.com PlaceId {pid} (campgrounds and "
                  f"site types, nv_places_2026-10-12.json), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NV findings")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:50], f["nightly_low"], f["surcharges"])
