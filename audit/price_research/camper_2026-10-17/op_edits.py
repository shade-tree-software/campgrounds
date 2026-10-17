#!/usr/bin/env python3
"""Website / name / note edits from the 2026-10-17 operator-site probe (live sites Campendium listed that our
records lacked), plus the note_scan re-stamp for the camper-priced notes build.py wrote. Run once."""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from edit_entries import edit
from extract_fields import note_sig

def web(e, url, drop=()):
    old = [x for x in (e.get("website") or "").split("\n") if x.strip() and x.strip() not in drop]
    e["website"] = "\n".join([url] + [x for x in old if x != url])

def note(e, old, new):
    assert e["note"].count(old) == 1, (e["id"], old)
    e["note"] = e["note"].replace(old, new)

def add(e, sent):
    n = e["note"].rstrip()
    e["note"] = (n[:-len("--Claude")].rstrip() + " " + sent + " --Claude") if n.endswith("--Claude") else (n + " " + sent + " --Claude")

F = {}
def f1269(e):
    web(e, "http://www.treehavencampground.site/")
    note(e, "Season May-Nov. No standalone website (county tourism/booking listings).", "Season May 1-Oct 31; call to book.")
    return e
def f4239(e):
    web(e, "http://hillbillycampground.com/")
    note(e, "Laundry, showers, store.", "Laundry, showers, store. Open May 1-Nov 1; rigs to 33-ft trailers / 35-ft motorhomes, no tents.")
    return e
def f6723(e):
    web(e, "https://longlakeresort.com/rv-camping/"); return e
def f7690(e):
    e["name"] = "Cub Country RV Park"
    web(e, "https://cubcountryrv.com/", drop=("https://www.facebook.com/overyonderrvpark/",))
    note(e, "22-site full-hookup RV park (formerly Gandys Springcreek)", "22-site full-hookup RV park (formerly Over Yonder RV Park, and before that Gandys Springcreek)")
    return e
def f8094(e):
    web(e, "http://www.billythekidmuseumfortsumner.com/rv-park.html")
    note(e, "Call to book.", "Booked by phone through the museum.")
    return e
def f8729(e):
    web(e, "https://riprapcamp.com/"); return e
def f11508(e):
    web(e, "https://coloradoriveroasis.com/")
    e["phone"] = "928-763-4385"
    note(e, "Small (~36-site) transient RV park", "~80-site RV park")
    add(e, "RVs must be 2000 or newer (older than 2010 pre-approved).")
    return e
def f14995(e):
    web(e, "https://crowsnestpasscamp.com/")
    add(e, "Seasonal: closed Nov 1, 2025 to May 1, 2026.")
    return e
# live operator page, no rate posted: the camper report goes in the note only, no price (AWH 2026-10-11)
def f1978(e):
    web(e, "https://parkwith.us/camps/saline-creek-rv-park-and-campground")
    add(e, "Its booking page posts no rate; campers reported paying $40-44 a night (Campendium, July 2024 and August 2025).")
    return e
def f2068(e):
    web(e, "https://bookingsus.newbook.cloud/online/sterett_creek?place_booking")
    add(e, "Books online through Unhitched RV; campers reported paying $50 a night (Campendium, July 2024).")
    return e
def f5110(e):
    e["name"] = "Magic River Campground"
    web(e, "https://www.magicrivercampground.com/")
    add(e, "Its website posts no rate; campers reported paying $30-36 a night (Campendium, October 2024 and September 2025).")
    return e
def f6959(e):
    web(e, "https://sugarhillrvpark.com/")
    note(e, "No dedicated website (Facebook only).", "Its website takes availability requests but posts no rate; a camper reported paying $19 a night (Campendium, January 2025).")
    return e
def f13063(e):
    web(e, "https://www.docksidemotel.ca/rv-park/")
    add(e, "Run by the Dockside Motel; a camper reported paying $40 a night in August 2026 (Campendium, currency not stated).")
    return e
def site(url):
    def f(e):
        web(e, url); return e
    return f
F.update({1269: f1269, 4239: f4239, 6723: f6723, 7690: f7690, 8094: f8094, 8729: f8729, 11508: f11508,
          14995: f14995, 1978: f1978, 2068: f2068, 5110: f5110, 6959: f6959, 13063: f13063,
          2878: site("https://www.ttmhospitality.com/sunset-motel-and-rv"),
          2070: site("https://gracecommunities.com/communities/the-last-resort/"),
          5099: site("https://fourseasonsrvpark.weebly.com/"),
          7775: site("https://sandypinesrvpark.com/"),
          10520: site("http://www.elmarvpark.com/")})
# build.py's 37 camper-priced notes: the added sentence is the rate already in fees -> nothing to re-derive
camper = [int(l.split("|")[0]) for l in open(os.path.join(HERE, "rows.txt")) if l.strip() and not l.startswith("#")]
def restamp(e):
    if e.get("note_scan"):
        e["note_scan"] = {"sig": note_sig(e["note"]), "checked": datetime.date.today().isoformat(), "model": "claude-opus-5-5/session"}
    return e
for i in camper:
    F.setdefault(i, restamp)
edit(F, note_rescanned=True)
print(len(F), "entries edited")
