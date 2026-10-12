"""Louisiana State Parks findings: each park's camping rates on its lastateparks.com page (la_park_rates_2026-10-12.json;
the site refuses plain fetches, read through the one-browser driver) and the booking site's own unit records
(la_booking_sites_2026-10-12.json, the `var sites = [...]` array on each reservations.gooutdoorslouisiana.com
FacilityDetails page: type, max equipment length, base price).

    python3 -I la_build.py OUT

Every park prices by demand: 'Campsite rates subject to change depending on availability', each type from its base to
1.5 times it (Premium $33 - $49.50, Improved $28 - $42, Unimproved $18 - $27, plus tax), and the booking site's base
prices are the pages' low ends. So nightly_low / nightly_high are the base type's range, there is no fixed weekend
add-on, and the hookup add-ons are the differences between the types' low ends. What a type includes differs by park
and is taken from the page: Improved is water and electric everywhere; Premium is full hookups at some parks and
water-and-electric 'prime location' or pull-through sites at others. An Unimproved site is the base only where the
booking site shows unimproved sites long enough for a 23-ft rig (Fontainebleau, Tickfaw); elsewhere they are tent
sites or too short. 'A $4.50 non-refundable fee will be assessed on each reservation transaction'. America the
Beautiful Senior and Access pass holders get 50% off camping if their home state's parks honour the pass."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
pages = json.load(open(os.path.join(HERE, "la_park_rates_2026-10-12.json"), encoding="utf-8"))["parks"]
booking = json.load(open(os.path.join(HERE, "la_booking_sites_2026-10-12.json"), encoding="utf-8"))["facilities"]
TYPE = re.compile(r"(\d+) (Premium|Improved|Unimproved)(?: Pull-Through)? Campsites \$([\d.]+)\s*-?\s*\$([\d.]+)/night plus tax "
                  r"(.*?) Book Now")
def money(v):
    return f"${v:.0f}" if float(v).is_integer() else f"${v:.2f}"
out, flags = [], []
for eid, p in sorted(pages.items(), key=lambda kv: int(kv[0])):
    eid = int(eid)
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    text = p["camping"].split("Equestrian Area Campground")[0]          # Bogue Chitto's horse camp is not a camping option here
    types = [{"n": int(n), "kind": k, "low": float(lo), "high": float(hi), "desc": d.strip(),
              "sewer": bool(re.search(r"(?i)sewer", d))} for n, k, lo, hi, d in TYPE.findall(text)]
    if not types:
        flags.append((eid, e["name"], "no campsite rates on the page")); continue
    fac = (re.search(r"facID=(\d+)", e.get("website") or "") or [None, None])[1]
    fit_u = [s for s in (booking.get(fac, {}).get("sites") or []) if s.get("UnitType") == "Campsite Unimproved"
             and s.get("IsActive") and 23 <= (s.get("MaxEquipLength") or 0) < 999]
    usable = [t for t in types if t["kind"] != "Unimproved" or fit_u]
    base = min(usable, key=lambda t: (t["low"], t["sewer"]))
    sur = {}
    hook = [t for t in usable if t["kind"] in ("Improved", "Premium") and not t["sewer"] and t is not base]
    sewer = [t for t in usable if t["sewer"] and t is not base and not base["sewer"]]
    if base["kind"] == "Unimproved" and hook:
        sur["electric"] = round(min(t["low"] for t in hook) - base["low"], 2)
    if sewer:
        sur["full_hookup"] = round(min(t["low"] for t in sewer) - base["low"], 2)
    prem = [t for t in usable if t["kind"] == "Premium" and not t["sewer"] and base["kind"] == "Improved"]
    if prem:
        sur["premium_site"] = round(min(t["low"] for t in prem) - base["low"], 2)
    parts = [f"{t['n']} {t['kind'].lower()} sites {money(t['low'])}-{money(t['high'])} ({t['desc'].rstrip('.')})" for t in types]
    note = ("; ".join(parts) + ". Prices rise with demand to the top of each range; plus tax. " +
            (f"The unimproved sites here are tent sites or too short for a 23-ft rig. " if any(t["kind"] == "Unimproved" for t in types) and not fit_u else "") +
            "$4.50 reservation fee per booking. America the Beautiful Senior and Access pass holders get 50% off camping "
            f"if their home state's parks honour the pass. Louisiana State Parks' park page and booking site, read {D}.")
    fees = {"nightly_low": base["low"], "nightly_high": base["high"], "currency": "USD", "reservation_fee": 4.5,
            "checked": "2026", "note": note}
    if sur:
        fees["surcharges"] = sur
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{p['url']} (camping rates, 'subject to change depending on availability', 'A $4.50 non-refundable fee "
                          f"will be assessed on each reservation transaction') + reservations.gooutdoorslouisiana.com"
                          f"/FacilityDetails.aspx?facID={fac} (unit records), read {D}" if fac else
                          f"{p['url']} (camping rates; '$4.50 non-refundable fee' per reservation), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "LA findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:32], f["nightly_low"], f["nightly_high"], f.get("surcharges"), "|", f["note"][:200])
for fl in flags:
    print("FLAG", *fl)
