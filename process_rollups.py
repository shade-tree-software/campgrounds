#!/usr/bin/env python3
"""Draft a short write-up for each day of a trip.

The first part of the trip archive whose output is a judgement call rather than
a verifiable answer: it assembles everything known about a day — the GPS, the
campground, the photos and whatever the family wrote on them — and asks Claude
for a few sentences.

    python process_rollups.py --trip 95 --dry-run   # see the facts, no API call
    python process_rollups.py --trip 95             # draft one trip
    python process_rollups.py                       # draft every day missing one
    python process_rollups.py --force --trip 95     # redo (keeps hand edits)

**Start with --dry-run.** It prints the dossier each day would be written from
and costs nothing. Garbage in is confabulation out, so the dossier is the half
worth checking first; the prose is easy to judge and cheap to redo.

**A day nobody wrote a word about still gets an entry**, from facts alone — the
GPS knows the route, the mileage and the stops, and the campground record knows
where you slept. That is deliberate: captions and notes should make a day
better, not decide whether it gets written at all, and it is what lets the
whole back catalogue be covered.

**The constraint against invention is the point of this script.** A model handed
facts will write fluent prose and will also invent connective tissue — the
crisp mountain air, the sense of relief — that reads fine today and is
unfalsifiable in twenty years. The system prompt forbids it, the dossier gives
nothing to embroider, and every rollup is stamped with the model that wrote it
so a generated sentence is never mistaken for something you said.

**A hand-edited rollup is never overwritten**, not even by --force; the app sets
`edited` when you fix one.

**Two rules decide when a day is drafted, and together they are what makes an
unattended run safe to schedule:**

  - *Only when its facts have moved.* Each entry stores `inputs_sig`, a hash of
    the narrow set a summary is actually built from — the day's driving and the
    campspots that bound it (`day_signature`). A trip gathers hundreds of edits
    during it and for weeks after; none of them touch that set, so a nightly run
    over the whole library normally drafts nothing and costs nothing. When the
    mileage or a campspot really does change, that day alone is redrafted.
  - *Only once its GPS has stopped moving.* An in-progress trip re-polls the
    tail of its track, so a day inside that window can still gain distance
    (`day_settled`). Days that aren't settled are held back and reported rather
    than written up early and wrongly. `--ignore-settle` overrides.

Needs: pip install -r tools_requirements.txt, and ANTHROPIC_API_KEY in the
environment or in the repo's gitignored .env.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
from datetime import date as _date, datetime, timedelta

from trips import event_time_rank, reference_timezone

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

ROLLUPS_FILE = os.path.join(_DIR, "trip_data", "day_rollups.json")

MODEL = "claude-opus-5"

# Fallback only. main() reads the real number off ekko_trips_app so the two
# can't drift; this is what day_settled() uses when called without the app
# loaded (the tests do that).
SETTLE_AFTER_S = 48 * 3600

# Short on purpose. The failure mode is padding: given four facts and room for
# three hundred words, a model reaches for atmosphere. A tight ceiling makes
# "not much happened" an available answer.
# 16000, the documented default for a non-streaming request — NOT a ceiling
# chosen to match the length of an entry. Adaptive thinking is on by default on
# Opus 5 and its tokens come out of this same budget, so a low cap does not
# produce a short entry; it produces a TRUNCATED one. At 700 the two richest
# days of trip 95 stopped mid-sentence ("where US-34 — our compan") and were
# written to the file as though complete, because nothing checked stop_reason.
MAX_TOKENS = 16000

SYSTEM = """You write ONE SHORT PARAGRAPH about one day of a family's camping \
trip, from a dossier of facts. It sits above that day's own timeline cards on \
the page, as a subtitle to them.

WHAT IT IS FOR. A first-time reader scrolling the trip wants to know what kind \
of day this was before they read the individual stops. That is the only job. \
The cards below already list every stop, photo, campsite and note, so anything \
you name from them is wasted words — the reader is about to read it anyway.

RULES, in order of importance:

1. THE SHAPE OF THE DAY IS THE CONTENT. How far, which way, across what, and \
what kind of day that made — a haul, a touring day, a moving day, a day that \
barely moved, the turn for home. That is what the cards below cannot say and a \
reader cannot assemble for themselves.
   ON A DAY THAT BARELY DROVE, WHAT HAPPENED IS THE SHAPE. Mileage is the \
least interesting fact about a day spent at one place, and a summary that \
leads with it says nothing at all. Lead with where the day was based and what \
it was spent on; the distance, if it earns a mention, comes last or not at all.
2. AS SHORT AS THE DAY IS. 45 words is a ceiling, not a target, and plenty of \
days want far fewer — a day with one thing in it gets one clause, not a \
sentence padded out to length. "North for the new year, 188 miles out of \
Virginia through Maryland to the Svendsens'" is a complete entry. Never add \
words to reach a length.
3. IMPERSONAL VOICE. Never "we", "our" or "I". The family's own words are all \
over the page already; this stands above them as a different kind of text, and \
the reader should be able to tell in one glance which is which. Write "a short \
evening run west", not "we drove west".
4. NAMES YES, DESCRIPTIONS NO. Name what the dossier names: the day\'s \
"events", its "family_visits", and the campground in "from"/"to". A name \
orients a reader; it is not a retelling, and withholding it is what left a \
day at one campground with nothing to say but its mileage.
   What you must NOT do is reproduce what the cards say ABOUT those things: no \
descriptions, no photo captions, no campsite notes, no site numbers, no photo \
counts, no people beyond a family visit\'s own label. The dossier does not \
carry them, and you must not invent them to fill the gap — naming a place is \
the end of what you know about it.
   Minor stops — fuel, rest areas, pull-offs — are not in the dossier in any \
form, not even as a count. Do not speculate about them or about how busy a \
day was beyond what "events" shows. If something mattered, it is an event.
5. NEVER REMARK ON WHAT THE RECORD DOES OR DOESN'T HOLD. No "the only thing \
recorded", "nothing else on the day", "nothing but the drive", "with nothing \
on it at all". That is commentary about the archive rather than about the day, \
it draws attention to a thin day instead of letting it be brief, and it is the \
single most common way these entries go wrong. Name what there is and stop.
6. EVERY FACT FROM THE DOSSIER. The mileage, the states, the driving time and \
the day's place in the trip are given. Do not invent terrain, weather, mood, \
fatigue, or why anything took as long as it did. "states" is the ordered list \
of states the day drove through, so "across Pennsylvania, a corner of West \
Virginia and the whole width of Ohio into Indiana" is supported and anything \
about what those states LOOKED like is not.
7. USE "trip_outline" TO PLACE THE DAY. It is every day of the trip in order \
with its distance and where it slept, so you can see whether this was the \
biggest day, the first easy one after a run of hauls, a second night at the \
same campground, or the highest the trip reached. Saying where a day sits in \
the trip is the most useful thing you can do with 40 words, and on a day with \
no distance of its own it is often the ONLY comparison available.
   A null "miles" is a day with no travel distance — never recorded, or based \
at one campground — and NOT a small distance. Never read a null as a low \
number or as evidence the trip paused.
   The outline is for placing THIS day. Do not narrate other days or restate \
their numbers, and do not say what happened on them — you are not told what \
happened on them, only how far they went and where they stopped.
8. "left_at" AND "arrived_at" ARE WHEN THE TRAVELLING STARTED AND FINISHED, \
local time, and they are the shape of a travel day. A day that leaves at 14:00 \
spent its morning somewhere — say so ("at the Svendsens' until mid-afternoon, \
then the drive home") rather than writing it up as though it were all road. \
Describe them in plain words — first thing, mid-morning, mid-afternoon, into \
the evening — never as clock times. Absent means the day never left one place.
9. PLAIN LANGUAGE. No brochure words: nothing is nestled, stunning, scenic, \
breathtaking or a hidden gem. No exclamation marks. Plain past tense.
10. ON A "round_trip" DAY, DO NOT MENTION DRIVING AT ALL. The day began and \
ended in the same place, so it was BASED there and the "events" are what it \
was for — write about those. No distance is given for such a day and you must \
not estimate, imply or allude to one: no "a short drive out", no "loops", no \
"a few miles". A round-trip day with no events at all was a quiet one at camp; \
say that plainly and briefly.
11. ABSENT MILEAGE IS NOT ZERO MILEAGE. If "mileage" says not recorded, the \
distance is unknown and you must not say the day had no driving, was parked, \
or stayed put — read "moved" instead, and if it is true describe the move \
without a figure. Only "driving": "negligible" or a matching "from" and "to" \
license saying the day stayed in one place.
12. Do not restate the date, the weekday, the trip name or the day number — \
the page already shows them.

WORKED EXAMPLES. These are the target, written by hand and approved. Match \
their length, voice and altitude, not their wording:

  520 miles, MD→PA→WV→OH→IN, day 2 of 14, the trip's longest:
  "The long haul: 520 miles and nine hours at the wheel, across Pennsylvania, \
a corner of West Virginia and the whole width of Ohio into Indiana. The \
biggest driving day of the trip."

  124 miles, MD only, day 1 of 14, next day 520:
  "A short evening run west to get the trip started — 124 miles into the \
Maryland mountains, with the real driving saved for tomorrow."

  405 miles, IL→IA, day 3 of 14, after two hauls, several real stops:
  "West across Illinois and over the Mississippi into Iowa. Still 405 miles, \
but the first day that felt like touring rather than hauling — a handful of \
real stops spaced through it."

  454 miles, IA→NE, day 4 of 14, ending at a reservoir campground in SW NE:
  "The rest of Iowa and most of Nebraska, 454 miles of country opening out and \
emptying as it went, ending at a reservoir in the southwestern corner of the \
state within reach of Colorado."

Return only the paragraph."""


# ── .env ──────────────────────────────────────────────────────────────────
def _load_dotenv():
    """Minimal .env loader, matching tests/smoke_select_track.py — the project
    deliberately doesn't depend on python-dotenv."""
    path = os.path.join(_DIR, ".env")
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _merge_and_write(updates):
    """Apply this run's deltas to the file on disk, per key.

    The app edits this file (a hand correction sets `edited`), so a long batch
    must not dump a stale snapshot over the top of an edit made while it ran.
    """
    current = _load(ROLLUPS_FILE)
    for key, fields in updates.items():
        current.setdefault(key, {}).update(fields)
    os.makedirs(os.path.dirname(ROLLUPS_FILE), exist_ok=True)
    tmp = ROLLUPS_FILE + f".{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, ROLLUPS_FILE)
    return current


# ── The dossier ───────────────────────────────────────────────────────────
def _fmt_time(t):
    return (t or "").strip()


# An admin unit is not a place anyone says out loud. Nominatim's reverse
# geocode falls through city → town → village → hamlet → municipality →
# township → county, so a point outside every town's polygon comes back as
# "Braxton County" or "Wharton Township" — 29% of the library's events. Handed
# to a writer that becomes "Bulltown Campground in Braxton County", which no
# traveller would ever write. Suppressing it yields silence, which is honest;
# saying "near Napier" needs the nearest-town lookup, which is a separate job.
_ADMIN_UNIT = re.compile(
    # Both shapes Nominatim hands back: a trailing type ("Larimer County",
    # "Wharton Township", "Bedminster Twp") and a leading one ("Municipality
    # of Anchorage", "Township of Washington").
    r"\b(county|parish|borough|township|twp\.?|municipality)$"
    r"|^(county|parish|borough|township|municipality)\s+of\b",
    re.IGNORECASE)


def _where(locale, state):
    """"<locale>, <ST>" — but only when the locale is a real named place.

    `trips.where_label` already carries the state when it has resolved the
    coordinate ("just outside Napier, WV"), so a value that already names the
    state passes through untouched; this stays as the guard for the stored
    `locale` it falls back to.
    """
    locale = (locale or "").strip()
    state = (state or "").strip()
    if _ADMIN_UNIT.search(locale):
        locale = ""
    if state and (locale == state or locale.endswith(", " + state)):
        return locale
    return ", ".join(x for x in (locale, state) if x)


# Distance and duration are already on the day divider beside the entry, and
# nobody recalls a day as "124 miles in 2h 24m". What prose can add is whether
# the day FELT like a haul, so the dossier carries a bucket and no numbers —
# the model cannot recite a figure it was never given. Bars are the library's
# own distribution over 242 A-to-B days (median 174, p75 234, p90 336): 300
# is comfortably a long day, 450 is a grind. A round trip out of camp is never
# worth mentioning however far it wandered.
DRIVE_LONG_MI = 300
DRIVE_VERY_LONG_MI = 450


def _drive_bucket(drive):
    if not drive or drive.get("round_trip"):
        return ""
    miles = drive.get("miles") or 0
    if miles >= DRIVE_VERY_LONG_MI:
        return "very long"
    return "long" if miles >= DRIVE_LONG_MI else ""


def _haversine_mi(lat1, lng1, lat2, lng2):
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = (math.sin(dp / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def _bearing(lat1, lng1, lat2, lng2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lng2 - lng1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _stay_point(stay):
    """(lat, lng) of a stay, or None. `enrich_trip_locations` has already
    resolved `campsite_location` over the campground's listed coords."""
    try:
        return float(stay["lat"]), float(stay["lng"])
    except (KeyError, TypeError, ValueError):
        return None


def _elevation_ft(stay, elevations):
    """Feet, because the app shows feet everywhere a human reads elevation.

    Only offered for where the day ENDED: "up into the mountains" is a fact
    about arriving somewhere, and giving both ends invites the model to narrate
    a climb whose profile it cannot see. It is also the ONLY licence the prompt
    gives for saying anything about terrain — rule 5 forbids inventing it, so
    without this every day reads as flat.

    Note `_load_locations_by_id()` cannot supply this: it trims entries to
    name/lat/lng/kind, so an elevation read from there is always None.
    """
    try:
        return round(float(elevations[stay["campground_id"]]) / 10) * 10
    except (KeyError, TypeError, ValueError):
        return None


def _heading(from_pt, to_pt):
    """Rough compass direction of the day's travel, or "" if it barely moved.

    The single most useful word in a one-line summary of a driving day and
    nowhere in the trip record — a reader places "west across Illinois" instantly
    and "Illinois to Iowa" not at all.
    """
    if not from_pt or not to_pt:
        return ""
    if _haversine_mi(*from_pt, *to_pt) < 15:
        return ""          # a day spent around one place has no heading
    brg = _bearing(*from_pt, *to_pt)
    return ["north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest"][round(brg / 45) % 8]


def states_crossed(track_day, samples=40):
    """The states the day drove through, in order, deduped.

    The fact the hand-written exemplars lean on hardest and the ONLY one that
    was not already somewhere in the trip record: a day's stops name the states
    it stopped in, which silently drops every state it merely drove across —
    trip 95's second day stopped in MD, PA and IN and also crossed a corner of
    West Virginia and the whole width of Ohio.

    Read from the GPS with the offline gazetteer (`nearest_town`), so it costs
    no API call and works on the USB build. Sampling rather than walking every
    ping is deliberate: a 6,000-ping day resolves in 40 lookups, and a state
    you were in for less time than the gap between samples is not one a reader
    needs told about. The nearest populated place's state can be wrong within a
    few miles of a border — accepted, because the alternative is a polygon set
    the repo does not carry, and a mislabelled border town changes one item in
    a list rather than inventing a fact.
    """
    if not track_day:
        return []
    try:
        import nearest_town as _nt
        _nt.load()
    except Exception:
        return []          # no gazetteer on this host: the day just loses states
    step = max(1, len(track_day) // samples)
    out = []
    for p in track_day[::step] + [track_day[-1]]:
        try:
            st = (_nt.nearest_town(p["lat"], p["lon"]) or {}).get("state")
        except Exception:
            continue
        if st and (not out or out[-1] != st):
            out.append(st)
    return out


def _day_moved(trip, day):
    """Did the day end somewhere other than it began, GPS or no GPS?

    Read off the stays, which exist whether or not a track does: waking and
    sleeping in different places means it moved, and so does having only one
    of the two (the drive out from home on day one, or the drive home on the
    last day).
    """
    woke = slept = None
    for stay in trip.get("stays", []):
        start, end = stay.get("start", ""), stay.get("end", "")
        if start < day <= end:
            woke = stay
        if start <= day < end:
            slept = stay
    if bool(woke) != bool(slept):
        return True
    if not woke:
        return False
    def where(s):
        return s.get("where_label") or s.get("place") or ""
    return where(woke) != where(slept)


def day_clock(pings, radius_m=1000):
    """When the day's travelling actually started and finished, local time.

    The shape of a travel day is not only its distance: leaving the Svendsens'
    at three in the afternoon and leaving at seven in the morning are different
    days, and nothing else in the dossier distinguishes them. AWH pointed at a
    New Year's Day summary that read as a pure driving day when most of it had
    been spent with family before setting off.

    Same rule `_drive_days` uses for the stats page, so the two agree about
    when a day's driving began: the LAST ping still within `radius_m` of where
    the day started is the departure, and the FIRST ping already within
    `radius_m` of where it ended is the arrival. A campground-sized radius,
    bounding by position rather than by mileage — an evening of GPS jitter at
    camp would otherwise keep the drive "running" for hours.
    """
    if len(pings or []) < 3:
        return {}
    import zoneinfo
    pts = sorted(pings, key=lambda p: p["tst"])
    a, b = (pts[0]["lat"], pts[0]["lon"]), (pts[-1]["lat"], pts[-1]["lon"])
    if _haversine_mi(*a, *b) * 1609.34 < radius_m:
        return {}                       # never left its own circle: not a travel day
    left = max((p for p in pts if _haversine_mi(p["lat"], p["lon"], *a) * 1609.34 <= radius_m),
               key=lambda p: p["tst"], default=None)
    arrived = min((p for p in pts if _haversine_mi(p["lat"], p["lon"], *b) * 1609.34 <= radius_m),
                  key=lambda p: p["tst"], default=None)
    out = {}
    for key, ping in (("left_at", left), ("arrived_at", arrived)):
        if not ping:
            continue
        try:
            tz = zoneinfo.ZoneInfo(ping.get("tz") or "UTC")
            out[key] = datetime.fromtimestamp(ping["tst"], tz).strftime("%H:%M")
        except Exception:
            pass
    return out


def day_dossier(trip, day, driving, elevations, day_states=None,
                trip_outline=None, day_index=None, track_known=True,
                day_times=None):
    """The facts one day's paragraph is written from, and nothing else.

    Deliberately much narrower than the dossier the long rollups used. That one
    carried the day's stops by name, their descriptions, the captions on their
    photos and the notes on the campground — and was assembled FROM the very
    cards printed directly below the write-up, so faithful prose could only
    restate them. It was rejected for exactly that.

    What is left is the part a reader cannot assemble by scrolling: how far,
    which way, across what, and where the day sits in the trip. Keeping the
    stop names OUT is not a saving, it is the feature — a model handed a list
    of places will name them.
    """
    d = {"date": day, "weekday": ""}
    try:
        d["weekday"] = _date.fromisoformat(day).strftime("%A")
    except ValueError:
        pass
    if day_index:
        d["day_of_trip"], d["trip_days"] = day_index
    if trip_outline:
        # Every day of the trip in order: its distance and where it slept. The
        # mileage alone supported the comparisons a reader values most ("the
        # biggest driving day", "the third of four days near four hundred
        # miles") but nothing about CONTINUITY — "a second day based at X",
        # "the first full day in the park", "the highest point of the trip"
        # all need to know what the OTHER days did, and none of them were
        # reachable from a list of numbers. Those are also disproportionately
        # the lines that carry a local day, which has no mileage to compare.
        #
        # Deliberately NOT the other days' events: a much larger payload, and
        # it invites writing about days that are not this one.
        d["trip_outline"] = trip_outline

    drive = driving.get(day) or {}
    if drive.get("round_trip"):
        # Out and back from one campground. The distance is deliberately NOT
        # offered, and the rule holds even when the day has few events and many
        # stops — the Trail Ridge case, where 54 miles of looping arguably WAS
        # the day. AWH 2026-09-11, on why it still shouldn't be mentioned:
        # "Mileage is interesting on a 502 mile day, not on a day when miles
        # just incidentally happened to add up due to a lot of local
        # activities." The test is whether the distance was the day's
        # achievement or its by-product, and round_trip is the proxy for that.
        # A figure in the dossier is a figure that ends up in the prose, so it
        # is withheld rather than forbidden. What the day was FOR is `events`.
        d["round_trip"] = True
    elif drive.get("miles"):
        d["miles"] = drive["miles"]
        if drive.get("moving"):
            d["driving_time"] = drive["moving"]
    elif track_known:
        # Measured, and it came out under `DRIVE_DAY_MIN_M` — the day really
        # did stay put. `_trip_driving_by_day` omits these rather than printing
        # "0 mi", which a reader would take as a measured zero.
        d["driving"] = "negligible — measured, the day stayed put"
    else:
        # NO TRACK AT ALL. Absence of a figure is not a figure of zero, and
        # conflating them is not hypothetical: on the first run of the back
        # catalogue this omission alone produced "the trip opened parked" for
        # a day that drove from home, and "a second day without driving" for
        # one that moved between two campgrounds 40 miles apart. Whether the
        # day moved is knowable without the GPS — the beds are in the trip
        # record — so it is stated outright rather than left to inference.
        d["mileage"] = "not recorded — no GPS for this day, distance unknown"
        d["moved"] = _day_moved(trip, day)
    if day_states:
        d["states"] = list(day_states)
    if day_times:
        # When the travelling actually started and finished. Two days of equal
        # distance are different days if one set off at seven and the other at
        # three, and nothing else here distinguishes them.
        d.update(day_times)

    # What HAPPENED, named but not described. The long rollups were rejected
    # for reproducing the descriptions, captions and notes printed on the cards
    # below — but a NAME is not a description, and withholding it left a local
    # day with nothing to say but its mileage, which on a day that barely drove
    # is the least interesting fact available.
    #
    # WAYPOINTS ARE NOT HERE AT ALL, not even as a count (AWH 2026-09-11): "If
    # a stop is interesting, it's my job to mark it as an event rather than a
    # waypoint, not the model's job to reinterpret." A count could only be
    # characterised by guessing what was at them — seven scenic overlooks and
    # seven fuel stops are the same integer — so the honest move is to let the
    # event/waypoint flag, which a person sets, be the whole answer.
    events, family = [], []
    for item in trip.get("timeline", []):
        if item.get("type") != "event" or item.get("sort_date") != day:
            continue
        if item.get("family_visit"):
            if item["family_visit"] not in family:
                family.append(item["family_visit"])
        elif not item.get("waypoint") and item.get("name") not in events:
            if item.get("name"):
                events.append(item["name"])
    if events:
        d["events"] = events
    if family:
        d["family_visits"] = family

    woke = slept = None
    for stay in trip.get("stays", []):
        start, end = stay.get("start", ""), stay.get("end", "")
        if start < day <= end:
            woke = stay
        if start <= day < end:
            slept = stay

    # Named as well as placed. The name was withheld while the only thing a
    # summary could say was how far it drove; once a day is allowed to say
    # what happened in it, "based at X for a second day" is the sentence a
    # reader of a local day actually wants.
    if woke:
        entry = {k: v for k, v in (
            ("place", woke.get("place")),
            ("where", _where(woke.get("where_label") or woke.get("locale"),
                             woke.get("state")))) if v}
        if entry:
            d["from"] = entry
    if slept:
        entry = {k: v for k, v in (
            ("place", slept.get("place")),
            ("where", _where(slept.get("where_label") or slept.get("locale"),
                             slept.get("state"))),
            ("elevation_ft", _elevation_ft(slept, elevations))) if v}
        if entry:
            d["to"] = entry

    if not d.get("round_trip"):
        heading = _heading(_stay_point(woke) if woke else None,
                           _stay_point(slept) if slept else None)
        if heading:
            d["heading"] = heading
    return d


def track_is_trustworthy(A, trip, pings):
    """Does this trip's GPS actually belong to it?

    The same gate the maps use (`_track_covers_trip`): at least one ping within
    `TRACK_NEAR_STAY_KM` of a stay or event. A trip the detail map refuses to
    draw a line for must not have its write-up built from that line either.

    Trip 43 is why. Its campspot is the Grove City KOA in Pennsylvania and its
    track never leaves Northern Virginia — the phone stayed home. The dossier
    reported `states: ["VA"]` and `driving: negligible`, which is not a thin
    fact but a false one, and a drafter would have written a quiet weekend at
    home for a trip to another state. Wrong data is worse than absent data,
    and absent is what this turns it into.
    """
    if not pings:
        return False
    # `_map_config()` is how every other caller gets home — it returns
    # (home, family) and is cached on the config mtimes.
    try:
        home, _fam = A._map_config()
        return bool(A._track_covers_trip(trip, pings, home))
    except Exception:
        return True          # can't judge: leave the track alone


def _track_by_local_day(A, trip_id):
    """The trip's GPS pings grouped by the local day they happened on.

    Bucketed by each ping's OWN timezone (`_local_date_of_ping`), the same rule
    the timeline and the driving stats use — otherwise an evening of westward
    driving lands on the next day and the states come out in the wrong day's
    list. Returns {} when the trip has no track, which just means those days
    carry no "states".
    """
    out = {}
    try:
        for ping in A._load_trip_track_for_detection(trip_id) or []:
            out.setdefault(A._local_date_of_ping(ping), []).append(ping)
    except Exception:
        return {}
    return out


def _prompt(dossier):
    """The dossier as JSON. Deliberately not prose: a model handed prose tends
    to echo its phrasing, and the point is for it to write from facts."""
    return ("Facts for one day. Write the entry.\n\n"
            + json.dumps(dossier, indent=2, ensure_ascii=False))


# ── When to draft, and when not to bother ─────────────────────────────────
def day_signature(trip, day, driving):
    """Fingerprint ONLY the facts a day's write-up is built from.

    How narrow this is decides whether the drafter can run unattended at all.
    A trip collects hundreds of edits while it happens and for weeks after —
    photos, captions, descriptions, waypoints, notes, reordering — and
    **not one of them is an input to a summary**, which says what kind of day
    it was: how far, which way, what sort of country, where you slept. Hash
    something wider and every one of those edits reads as a reason to rewrite
    prose nobody asked to have rewritten, at a cost per day, forever.

    So this deliberately does NOT reuse `_trip_route_signature`. That one
    hashes the whole raw trip record, which is right for a route — it depends
    on anchors and overrides scattered all through the record — and exactly
    wrong here: it changes on every edit.

    **If the dossier is ever widened toward captions or descriptions, widen
    this with it.** A dossier field that isn't in here is one the drafter will
    never notice has changed.
    """
    nights = []
    for stay in trip.get("stays", []):
        start, end = stay.get("start", ""), stay.get("end", "")
        if not (start <= day < end or start < day <= end):
            continue
        nights.append([stay.get("place", ""),
                       stay.get("where_label") or stay.get("locale") or "",
                       stay.get("state") or "",
                       start, end])
    payload = {"v": 1, "day": day, "drive": driving.get(day), "nights": nights}
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def day_settled(day, now=None, settle_s=SETTLE_AFTER_S):
    """Has this day's mileage stopped moving?

    A day is drafted from its GPS, and an in-progress trip re-polls the tail of
    its track on every page load — `TRACK_REFETCH_OVERLAP_S` back from the
    newest ping — so a day still inside that window can gain distance after it
    is over. Drafting one then means writing "312 miles" about a day that ends
    up at 400, and the entry reads as finished either way.

    Measured from the END of the day rather than from the trip's end, so one
    rule covers both cases: a finished trip's days are all long settled, and a
    trip still happening can have the day before yesterday written up while
    today is still being driven.
    """
    try:
        ends = datetime.combine(_date.fromisoformat(day), datetime.min.time()) \
            + timedelta(days=1)
    except (ValueError, TypeError):
        return False          # undated: never settled, so never drafted
    return (now or datetime.now()) >= ends + timedelta(seconds=settle_s)


# ── Days of a trip ────────────────────────────────────────────────────────
def trip_days(trip):
    """Every date the trip's own timeline mentions, in order."""
    days = set()
    for stay in trip.get("stays", []):
        for key in ("start", "end"):
            if stay.get(key):
                days.add(stay[key])
    for evt in trip.get("events", []):
        if evt.get("date"):
            days.add(evt["date"])
    return sorted(days)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trip", type=int, help="only this trip id")
    ap.add_argument("--force", action="store_true",
                    help="redraft days that already have a rollup "
                         "(hand-edited ones are still kept)")
    ap.add_argument("--force-edited", action="store_true",
                    help="also overwrite rollups a human has edited")
    ap.add_argument("-n", "--dry-run", action="store_true",
                    help="print the dossiers and stop — no API call, no cost")
    ap.add_argument("--ignore-settle", action="store_true",
                    help="draft days whose GPS may still be settling "
                         "(default: hold them back — see day_settled)")
    ap.add_argument("--limit", type=int, help="stop after this many days")
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()

    _load_dotenv()
    import ekko_trips_app as A

    # One number, owned by the app: the track re-fetch window IS the settle
    # window, and a copy here would drift the day someone tuned it.
    settle_s = getattr(A, "TRACK_REFETCH_OVERLAP_S", SETTLE_AFTER_S)

    trips = [t for t in A.parse_trips()
             if t.get("start") and not t.get("home_only")]
    if args.trip is not None:
        trips = [t for t in trips if t["id"] == args.trip]
        if not trips:
            print(f"no such trip: {args.trip}", file=sys.stderr)
            return 1

    # id -> feet. _load_campgrounds() already converts and is cached; the raw
    # file carries metres and the trimmed locations index carries neither.
    elevations = {c["id"]: c["elevation_feet"] for c in A._load_campgrounds()
                  if c.get("elevation_feet") is not None}
    rollups = _load(ROLLUPS_FILE)

    jobs = []
    held = 0
    stamps = {}
    for trip in trips:
        A.enrich_trip_locations(trip)
        driving = A._trip_driving_by_day(trip)
        days = trip_days(trip)
        # Every day's mileage in order — what lets the model say "the biggest
        # driving day of the trip" without being told which day that was.
        #
        # `None`, never 0, for a day with no travel distance — unrecorded or
        # round-trip alike. The same absent-vs-zero trap as the per-day
        # `mileage` field, and it bit the same way one fix later: with zeros
        # here the model read trip 47 as "two days of staying put" when the
        # second of them moved between campgrounds.
        def _slept_on(d):
            for st in trip.get("stays", []):
                if st.get("start", "") <= d < st.get("end", ""):
                    return st
            return None
        outline = []
        for n, dd in enumerate(days, 1):
            e = driving.get(dd) or {}
            st = _slept_on(dd)
            row = {"day": n,
                   "miles": None if e.get("round_trip") else (e.get("miles") or None),
                   "slept": (st or {}).get("place") or None}
            ft = _elevation_ft(st, elevations) if st else None
            if ft:
                row["elevation_ft"] = ft
            outline.append(row)

        # The track is read ONCE per trip and bucketed by local day. Only
        # pulled when there is actually something to draft, because a trip
        # whose days all have current rollups should cost nothing at all.
        # `None` means not yet loaded; `{}` means loaded and unusable.
        track_by_day = None

        for day_i, day in enumerate(days, 1):
            key = f"{trip['id']}/{day}"
            existing = rollups.get(key) or {}
            # NOTHING here is immune to being redrafted, and that is
            # deliberate (AWH 2026-09-11). `source: "conversation"` used to
            # outrank --force, on the reasoning that hand-written text
            # shouldn't be clobbered — but it is LLM text either way, and the
            # cost of freezing it is a library that cannot respond to its own
            # facts being corrected: promote a waypoint to an event, fix a
            # campspot date, re-fetch a track, and the day that should change
            # silently keeps its old prose forever. Provenance without
            # immunity: `source` still records who wrote it.
            #
            # The human channel is `day_notes` on the trip record, which needs
            # no protection here because it outranks every rollup at display
            # time (`_trip_day_writeups`). `edited` is vestigial — the app
            # writes a note OVER a draft rather than editing it, so nothing
            # sets the flag any more; the check stays as a cheap guard in case
            # something ever does.
            if existing.get("edited") and not args.force_edited:
                continue
            sig = day_signature(trip, day, driving)
            # A rollup written before signatures existed has none. Absence
            # means "legacy", not "changed" — read the other way, the first
            # run after this shipped would redraft the entire library.
            legacy = existing.get("text") and not existing.get("inputs_sig")
            stale = (existing.get("text") and existing.get("inputs_sig")
                     and existing["inputs_sig"] != sig)
            if existing.get("text") and not (args.force or args.force_edited
                                             or stale):
                if legacy:
                    stamps[key] = {"inputs_sig": sig}   # free, no API call
                continue
            if not (args.ignore_settle or day_settled(day, settle_s=settle_s)):
                held += 1
                continue
            if track_by_day is None:
                track_by_day = _track_by_local_day(A, trip["id"])
                pings_all = [p for v in track_by_day.values() for p in v]
                if pings_all and not track_is_trustworthy(A, trip, pings_all):
                    # The track belongs to something else — the phone stayed
                    # home, or roamed on the trip's dates without ever reaching
                    # the itinerary. The maps refuse to draw it; the dossier
                    # refuses to describe it. Dropping it here turns wrong
                    # facts into absent ones: no states, no clock, and a day
                    # with no mileage reports "not recorded" rather than
                    # "measured, stayed put".
                    print(f"  [{trip['id']}] track does not cover this trip — "
                          f"no states or times will be offered", file=sys.stderr)
                    track_by_day = {}
            pings = track_by_day.get(day, [])
            jobs.append((key, trip, day, sig,
                         day_dossier(trip, day, driving, elevations,
                                     states_crossed(pings), outline,
                                     (day_i, len(days)), bool(pings),
                                     day_clock(pings))))

    if args.limit:
        jobs = jobs[:args.limit]
    held_note = (f" {held} day(s) held back — GPS not settled yet."
                 if held else "")
    # Dry run must cost nothing and change nothing, stamps included.
    if stamps and not args.dry_run:
        _merge_and_write(stamps)
        print(f"Stamped {len(stamps)} existing rollup(s) with an input "
              f"signature (no API calls).")
    if not jobs:
        print("Nothing to draft — every day already has a current rollup."
              + held_note)
        return 0
    print(f"{len(jobs)} day(s) to draft.{held_note}\n")

    if args.dry_run:
        for key, _trip, _day, _sig, dossier in jobs:
            print(f"=== {key} ===")
            print(json.dumps(dossier, indent=2, ensure_ascii=False))
            print()
        print(f"(dry run — {len(jobs)} dossiers, no API calls, no cost)")
        return 0

    if not (os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        print("ANTHROPIC_API_KEY is not set. Put it in the repo's .env "
              "(export ANTHROPIC_API_KEY=sk-ant-...) or the environment.",
              file=sys.stderr)
        return 1

    import anthropic
    client = anthropic.Anthropic()

    in_tok = out_tok = cached = 0
    written = failed = 0
    for i, (key, trip, day, sig, dossier) in enumerate(jobs, 1):
        try:
            resp = client.messages.create(
                model=args.model,
                max_tokens=MAX_TOKENS,
                thinking={"type": "adaptive"},
                # The system prompt is identical on every call, so caching it
                # turns 300-odd repeats of it into one.
                system=[{"type": "text", "text": SYSTEM,
                         "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": _prompt(dossier)}],
            )
        except Exception as e:
            print(f"  {key}: failed ({e})", file=sys.stderr)
            failed += 1
            continue
        if resp.stop_reason == "refusal":
            # stop_details is populated only for refusals; guard before reading.
            why = getattr(getattr(resp, "stop_details", None), "category", "")
            print(f"  {key}: refused{f' ({why})' if why else ''}", file=sys.stderr)
            failed += 1
            continue
        if resp.stop_reason == "max_tokens":
            # A truncated entry is worse than none: it reads as finished prose
            # until you reach the end of it, and it would be stored stamped
            # with the model as though it were complete.
            print(f"  {key}: hit max_tokens — entry would be truncated, skipping",
                  file=sys.stderr)
            failed += 1
            continue
        text = "\n".join(b.text for b in resp.content if b.type == "text").strip()
        if not text:
            failed += 1
            continue

        in_tok += resp.usage.input_tokens
        out_tok += resp.usage.output_tokens
        cached += getattr(resp.usage, "cache_read_input_tokens", 0) or 0
        _merge_and_write({key: {
            "trip_id": trip["id"], "date": day, "text": text,
            # Stamped so a generated sentence is never mistaken for one of
            # yours — the same generated-vs-human line waterfront_evidence
            # draws on campground data.
            "model": args.model,
            "generated_at": int(time.time()),
            # What this entry was drafted FROM. The next run redrafts the day
            # only if these facts moved (see day_signature).
            "inputs_sig": sig,
            "edited": False,
        }})
        written += 1
        print(f"  [{i}/{len(jobs)}] {key}\n      {text[:100]}"
              + ("…" if len(text) > 100 else ""))

    # Priced from the response's own usage rather than estimated, so the number
    # is what was actually spent.
    cost = (in_tok * 5 + out_tok * 25) / 1_000_000
    print(f"\nDrafted {written} day(s)" + (f", {failed} failed" if failed else "")
          + f". {in_tok:,} in / {out_tok:,} out tokens"
          + (f" ({cached:,} cached)" if cached else "")
          + f" ≈ ${cost:.2f}")
    return 1 if failed and not written else 0


if __name__ == "__main__":
    sys.exit(main())
