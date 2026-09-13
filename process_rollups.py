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

**The examples are the family's own day notes, chosen per day.** Each draft is
shown the four hand-written `day_notes` whose days are closest in SHAPE to the
one being written, each behind the dossier it came from. A note is nearly
always a day where the draft was read and found wanting, so writing one is how
you correct this script — no prompt edit, no redraft of anything else. The
first run after a note is added rebuilds the bank, which reads a track per
noted trip and asks the DEM for their high points; expect a couple of slow
minutes once, then it is cached. `--no-examples` and `--no-elevation` skip
those two respectively.

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

from trips import event_time_rank, get_day_notes, reference_timezone

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
2. AS SHORT AS THE DAY IS. 35 words is a HARD ceiling and most days want \
twenty to twenty-five — a day with one thing in it gets one clause, not a \
sentence padded out to length. "North for the new year, 188 miles out of \
Virginia through Maryland to the Svendsens'" is a complete entry. Never add \
words to reach a length. Every rule below tells you what you MAY say when it \
earns its place; none of them is a requirement to say it, and a day that \
triggers four of them still gets one sentence. When two facts compete, keep \
the one a reader could not have guessed and cut the other. If an entry runs \
long, the first things out are the times of day, the arrival, and the second \
half of any comparison.
3. IMPERSONAL VOICE. Never "we", "our" or "I". The family's own words are all \
over the page already — including, on some days, a note of their own in this \
very slot — and this stands above them as a different kind of text, which the \
reader should be able to tell in one glance. Write "a short evening run west", \
not "we drove west". The example entries below are the family's own writing \
and DO use "we"; match their length and altitude, never that.
4. TELL THE DAY IN CLOCK ORDER, AND SAY WHEN THINGS HAPPENED. Every event \
carries its "time"; "left_at" and "arrived_at" say when the travelling started \
and finished. Put them in the order they happened — an event before "left_at" \
is the morning at the place the day started, and writing it up after the drive \
tells the day backwards. Such an event is also not optional: a paddle on the \
lake before setting off is how the day began and belongs at the front of the \
sentence. Anchor what you name to the part of the day it fell in — in the \
morning, after lunch, in the afternoon, for dinner, at sunset — but ONLY where \
it changes how the day reads. A day with one stop on it does not need to be \
told it happened in the afternoon, and an arrival needs no hour at all: "in \
before eight", "reached in the evening", "away after midday" are three ways of \
spending words on nothing. Never quote the clock, in figures OR in words, and \
never exceed what the times support: an event at 19:30 lasting an hour is a \
short evening out, not a day spent somewhere.
5. NAMES YES, DESCRIPTIONS NO. Name what the dossier names: the day\'s \
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
6. NEVER REMARK ON WHAT THE RECORD DOES OR DOESN'T HOLD. No "the only thing \
recorded", "nothing else on the day", "nothing but the drive", "with nothing \
on it at all". That is commentary about the archive rather than about the day, \
it draws attention to a thin day instead of letting it be brief, and it is the \
single most common way these entries go wrong. Name what there is and stop.
7. TIME FOR A SHORT DRIVE, MILEAGE FOR A LONG ONE. A figure is worth printing \
when the distance was the day's achievement. Under about 130 miles it wasn't: \
give the driving time in words ("an hour and a half south", "two hours out of \
Virginia") or no figure at all, because "66 miles" tells a reader nothing they \
feel. From about 300 miles up, the mileage IS the fact — print it. In between, \
use whichever the day was actually about. A small figure may stand where the \
smallness is the point and the phrase is shorter for it — "a 24-mile hop down \
to Pohick Bay" says it in four words — but "South 66 miles to Casa Vargas" \
should have been "an hour and a half south to Casa Vargas". Never print both \
for the same leg, and never convert driving time into a pace or an average.
8. DO NOT GLOSS A SMALL DISTANCE. If the driving was trivial, leave it out \
altogether — no "barely out of town", "hardly moved", "a couple of miles", \
"no distance to speak of". "Fireworks at Franklin Park in Purcellville" is the \
whole entry; adding where it sits relative to home says nothing a reader \
wanted.
9. EVERY FACT FROM THE DOSSIER. The mileage, the states, the driving time, the \
elevations and the day's place in the trip are given. Do not invent weather, \
mood, fatigue, or why anything took as long as it did.
   TERRAIN IS ALLOWED ONLY WHERE THE DOSSIER MEASURES IT. Four fields, and \
nothing else: "to.elevation_ft" (how high the day ended), "high_point_ft" (the \
highest ground it covered — on a day based at one place this, not the \
campground, is where the day was spent), "to.waterfront" with "to.water" (the \
water the camp fronts, and its name when given), and "to.within" (the forest \
or park that contains it). Use them plainly: "climbing to 8,200 feet", "a \
riverside camp on the Satilla", "inside the Ocala National Forest". Anything \
NOT in those fields you do not know — not the name of a mountain range, a gap, \
a valley or a river, however confidently it comes to mind. Naming one you were \
not given is the worst thing you can do here, because it is unfalsifiable and \
sometimes right.
   "high_point_ft" IS THIS DAY'S FIGURE AND NOTHING ELSE. You are not told \
what height any other day reached, so you cannot say this was the highest of \
the trip, the highest camp, or higher than yesterday. Print the figure or \
leave it out.
   AT MOST ONE of the four in an entry, and only when it says something the \
campground's own name doesn't. "Gifford Pinchot State Park" already reads as a \
park beside water; adding "the lakefront at" spends three words on nothing. \
Use them where the fact is the point — the day that climbed, the camp whose \
river the name doesn't mention.
10. "states" IS AN ORDERED CROSSING, NOT A DESTINATION. It lists the states \
the day drove through in order, so the first one is where the day started and \
every one after it was crossed. A day whose states are ["SC", "GA"] went \
"through South Carolina and into Georgia" — writing it as "through Georgia" \
drops half the day. Name the crossing when it took more than one state, and \
skip it entirely when the day never left one.
11. PLACE THE DAY ONCE, AND ONLY WITH SOMETHING COUNTABLE. "trip_outline" is \
every day of the trip in order with its distance and where it slept, so you \
can see whether this was the biggest driving day, the third of four days near \
four hundred miles, the highest the trip reached, or a second night at the \
same campground. One such clause is worth the words. TWO IS NEVER WORTH IT, \
and a clause that interprets the trip instead of measuring it is worth \
nothing: no "the trip turns here from family visit to touring", "the arrival \
day", "the only day that stayed put", "the first of three days on the water", \
"far more day than drive". Those are a narrator talking about the itinerary. \
Say which day was longest or highest, or say nothing.
   A null "miles" is a day with no travel distance — never recorded, or based \
at one campground — and NOT a small distance. Never read a null as a low \
number or as evidence the trip paused. Do not narrate other days or restate \
their numbers; you are not told what happened on them.
12. "left_at" AND "arrived_at" ARE WHEN THE TRAVELLING STARTED AND FINISHED, \
local time, and they are the shape of a travel day. A day that leaves at 14:00 \
spent its morning somewhere — say so ("at the Svendsens' until mid-afternoon, \
then the drive home") rather than writing it up as though it were all road. \
Describe them in plain words — first thing, mid-morning, mid-afternoon, into \
the evening — never as clock times. Absent means the day never left one place.
   THE FIRST DAY OF A TRIP THAT LEAVES AFTER ABOUT FOUR IN THE AFTERNOON ON A \
WEEKDAY LEFT AFTER WORK, and "after work" is the phrase for it — a short \
evening run to get the trip started, not a driving day. Check "weekday" and \
"day_of_trip" before using it; a Saturday afternoon is just an afternoon.
13. PLAIN LANGUAGE. No brochure words: nothing is nestled, stunning, scenic, \
breathtaking or a hidden gem. No exclamation marks. Plain past tense.
14. ON A "round_trip" DAY, DO NOT MENTION DRIVING AT ALL. The day began and \
ended in the same place, so it was BASED there and the "events" are what it \
was for — write about those. No distance is given for such a day and you must \
not estimate, imply or allude to one: no "a short drive out", no "loops", no \
"a few miles". A round-trip day with no events at all was a quiet one at camp; \
say that plainly and briefly.
   NOR ITS ABSENCE. "No need to move the camper at all", "with the camper left
   exactly where it stood", "without moving an inch" — these mention driving by
   describing its absence, which is the same fault wearing a different coat, and
   they add nothing to "a full day based at Assateague". Say where the day was
   based and what was in it; the reader does not need telling that a day based
   somewhere did not also drive.
15. ABSENT MILEAGE IS NOT ZERO MILEAGE. If "mileage" says not recorded, the \
distance is unknown and you must not say the day had no driving, was parked, \
or stayed put — read "moved" instead, and if it is true describe the move \
without a figure. Only "driving": "negligible" or a matching "from" and "to" \
license saying the day stayed in one place.
16. Do not restate the date, the weekday, the trip name or the day number — \
the page already shows them.

FACTS ABOUT THIS FAMILY, true of every trip:

- THEY TRAVEL IN THE CAMPER AND NOTHING ELSE. There is no second car. Any
local drive longer than a walk was made in the camper, so never write it as
though the camper stayed on the pitch while they went off in something else —
no "leaving the camper at the campsite", no "the camper stayed put while...".
A day based somewhere still moved the camper if it went anywhere.

EXAMPLES. The message carries a few of the family's own write-ups for days of \
a similar shape, each behind the facts it was written from. They are the \
target for length, altitude and what is worth saying — not for wording, not \
for voice (see rule 3), and never for their places.

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


# What a campground SITS in, read off its own record. Precision over coverage:
# a wrong river is worse than no river, so the phrase must be a run of plain
# capitalised words ending in a feature type, inside ONE clause of the note —
# without the clause bound, "…Boundary Campground. USFS Cherokee National
# Forest" parses as a single four-word name. About a fifth of the database
# yields something; the rest simply doesn't say, and silence is the right
# answer there. `waterfront` itself is audited on every entry and carries the
# rest of the load — "riverfront" licenses "a riverside camp" with no name.
_CAPWORD = r"(?:St\.|Mt\.|Ste\.|[A-Z][a-z'’\-]+)"
_WATER_FEATURE = (r"(?:River|Lake|Creek|Reservoir|Bayou|Sound|Bay|Pond|Lagoon"
                  r"|Inlet|Slough|Beach|Harbor|Harbour)")
_PARK_FEATURE = (r"(?:National Forest|National Park|State Park|State Forest"
                 r"|National Recreation Area|National Seashore"
                 r"|National Monument|State Recreation Area"
                 r"|National Wildlife Refuge|Provincial Park)")
_WATER_RE = re.compile(rf"\b((?:{_CAPWORD} ){{0,2}}{_CAPWORD}) ({_WATER_FEATURE})\b")
_PARK_RE = re.compile(rf"\b((?:{_CAPWORD} ){{0,2}}{_CAPWORD}) ({_PARK_FEATURE})\b")
_NOT_WATERFRONT = {"", "not waterfront", "none", "unknown"}


def _norm_name(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _first_feature(rx, text, name):
    """The first match that isn't just the campground's own name again."""
    for clause in re.split(r"[.;:\n]", text):
        for m in rx.finditer(clause):
            full = f"{m.group(1)} {m.group(2)}"
            return None if _norm_name(full) in _norm_name(name) else full
    return None


def campground_context(cg):
    """`{waterfront, water, within}` for one campground — or {}.

    `waterfront` is the audited field verbatim ("riverfront", "lakeview"); the
    two names are parsed out of the entry's note. Water is only looked for when
    the entry is actually on water, so a lakeside town's name in a note about a
    dry campground can't become "on the lake".
    """
    if not cg:
        return {}
    name, note = cg.get("name") or "", cg.get("note") or ""
    hay = f"{name}. {note}"
    out = {}
    wf = (cg.get("waterfront") or "").strip().lower()
    if wf not in _NOT_WATERFRONT:
        out["waterfront"] = wf
        water = _first_feature(_WATER_RE, hay, name)
        if water:
            out["water"] = water
    within = _first_feature(_PARK_RE, hay, name)
    if within:
        out["within"] = within
    return out


# The DEM is free and keyless, but a lookup per day per run is still a request
# the second run shouldn't repeat, so answers are cached by the coordinates
# they were asked about.
ELEVATION_CACHE = os.path.join(_DIR, "trip_data", "day_elevation_cache.json")
# How far above both beds the day has to reach before the climb is worth a
# word. Deliberately conservative: a figure in the dossier is a figure that
# ends up in the prose, and "climbing to 500 feet" on a coastal day is worse
# than saying nothing. 800 ft keeps the Alleghenies and the Rockies and drops
# the piedmont.
HIGH_POINT_MIN_GAIN_FT = 800


def _even_samples(pings, samples):
    """Points spaced evenly ALONG THE DRIVE, interpolated between pings.

    Sampling every Nth ping instead samples by ping density, which is highest
    exactly where the day stopped moving — an hour parked at a rest area can
    outweigh a mountain pass. Spacing by distance also puts a point every mile
    or two on a short drive, which is what gives the crest a chance of being
    seen at all; the pass between two five-minute pings is invisible either
    way, and the answer is then honestly silent rather than wrong.
    """
    pts = [(float(p["lat"]), float(p["lon"])) for p in pings]
    if samples < 2 or len(pts) < 2:
        return pts[:1]
    cum, total = [0.0], 0.0
    for (a_lat, a_lon), (b_lat, b_lon) in zip(pts, pts[1:]):
        total += _haversine_mi(a_lat, a_lon, b_lat, b_lon)
        cum.append(total)
    if total <= 0:
        return pts[:1]
    out, j = [], 0
    for i in range(samples):
        want = total * i / (samples - 1)
        while j < len(cum) - 2 and cum[j + 1] < want:
            j += 1
        span = cum[j + 1] - cum[j]
        f = 0.0 if span <= 0 else (want - cum[j]) / span
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f,
                    pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f))
    return out


# Open-Meteo meters LOCATIONS rather than calls — 600 a minute — so a whole
# library run spends its budget in the first twenty seconds and then waits a
# minute per day. Pacing to a little under the cap turns "fire, 429, sleep 61s"
# into a steady drip: a back-catalogue pass costs about the arithmetic minimum
# (~13,000 locations, so ~30 minutes) instead of hours. The retry below stays
# as the backstop for a budget shared with something else.
#
# 400, measured: eleven 40-point batches go through and the twelfth is refused,
# so the real ceiling is ~440 a minute rather than the 600 the forecast API
# allows. A budget set just above it is the worst of both worlds — it overshoots
# once per window and pays the retry wait every time, which is how a
# back-catalogue run ended up at two and a half minutes per trip.
_ELEV_BUDGET_PER_MIN = 400
_elev_spent = []            # [(unix_time, locations)] within the last minute


def _pace_elevation(n):
    now = time.time()
    _elev_spent[:] = [(t, c) for t, c in _elev_spent if now - t < 60]
    while sum(c for _, c in _elev_spent) + n > _ELEV_BUDGET_PER_MIN and _elev_spent:
        time.sleep(max(0.1, 60 - (time.time() - _elev_spent[0][0]) + 0.5))
        now = time.time()
        _elev_spent[:] = [(t, c) for t, c in _elev_spent if now - t < 60]
    _elev_spent.append((time.time(), n))


def _fetch_max_elevation_m(coords, retry=True):
    """Highest of these points off the Open-Meteo DEM, or None.

    Open-Meteo, not Open-Elevation: every campground in the database was pinned
    against Open-Meteo, so a day's high point should come off the same DEM as
    the camp it is compared against (the two disagree by several metres).

    The free tier meters LOCATIONS rather than calls — 600 a minute — so a
    40-point day costs a fifteenth of the budget and a back-catalogue run walks
    straight into a 429. One wait-and-retry is enough to get through it; a
    second failure gives up quietly, and the day simply has no high point.
    """
    import urllib.error
    import urllib.request
    _pace_elevation(len(coords))
    url = ("https://api.open-meteo.com/v1/elevation"
           "?latitude=" + ",".join(f"{lat:.4f}" for lat, _ in coords)
           + "&longitude=" + ",".join(f"{lon:.4f}" for _, lon in coords))
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read())
        return max(float(x) for x in data["elevation"] if x is not None)
    except urllib.error.HTTPError as e:
        if e.code == 429 and retry:
            # The window is rolling, so waiting half of one frees about half
            # the budget — a full minute is twice what is needed.
            time.sleep(30)
            return _fetch_max_elevation_m(coords, retry=False)
    except Exception:
        pass
    return None


def day_high_point_ft(pings, bed_elevations=(), samples=40):
    """The highest ground the day covered, in feet — or None.

    The only terrain fact in the dossier that is MEASURED rather than
    remembered, and it exists because of one entry: a day spent on Trail Ridge
    Road near 12,000 feet was written up as "based at Moraine Park at 8,200
    feet", the elevation of the bed it left and returned to. The campground's
    height says where the day slept; this says where it went.

    Withheld unless it clears both beds by `HIGH_POINT_MIN_GAIN_FT`. A day that
    wandered 300 feet above camp did not climb anything, and a figure in the
    dossier is a figure that ends up in the prose.
    """
    pts = sorted(pings or [], key=lambda p: p["tst"])
    if len(pts) < 3:
        return None
    use = _even_samples(pts, samples)
    key = hashlib.sha1(json.dumps(
        [[round(lat, 3), round(lon, 3)] for lat, lon in use]).encode()).hexdigest()
    cache = _load(ELEVATION_CACHE)
    if key in cache:
        metres = cache[key]
    else:
        metres = _fetch_max_elevation_m(use)
        if metres is None:
            return None            # offline or rate-limited: no field, no cache
        cache[key] = metres
        tmp = ELEVATION_CACHE + f".{os.getpid()}.tmp"
        os.makedirs(os.path.dirname(ELEVATION_CACHE), exist_ok=True)
        with open(tmp, "w") as f:
            json.dump(cache, f)
        os.replace(tmp, ELEVATION_CACHE)
    feet = round(metres * 3.28084 / 100) * 100
    beds = [b for b in bed_elevations if b]
    if beds and feet - max(beds) < HIGH_POINT_MIN_GAIN_FT:
        return None
    return feet


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
    # Cardinals get a 60-degree bucket, diagonals 30. People say "south" for a
    # drive 28 degrees off south — AWH's own note for the 409-mile run to South
    # Carolina (bearing 208) says "South", where an even eight-point split says
    # southwest. The diagonals stay for the drives that really are diagonal:
    # home to western Pennsylvania is 42 degrees off north and reads
    # "northwest" to anyone who has driven it.
    for i, name in enumerate(("north", "east", "south", "west")):
        if min((brg - i * 90) % 360, (i * 90 - brg) % 360) <= 30:
            return name
    return ["northeast", "southeast", "southwest", "northwest"][
        int(brg // 90)]


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


def day_anchors(trip, day, home_pt=None, day_index=None):
    """(where the day started, where it ended) — the beds, not the pings.

    Home is the missing end on the day a trip leaves and the day it comes
    back: neither has a stay at both ends, and both need one, for the compass
    (`_heading`) and for the clock (`day_clock`) alike. Only substituted on
    those two days — a mid-trip day with no stay is a gap in the record, not a
    night at home.
    """
    woke = slept = None
    for stay in trip.get("stays", []):
        start, end = stay.get("start", ""), stay.get("end", "")
        if start < day <= end:
            woke = stay
        if start <= day < end:
            slept = stay
    first_day = (day_index or (0, 0))[0] == 1
    last_day = day_index is not None and day_index[0] == day_index[1]
    return (_stay_point(woke) if woke else (home_pt if first_day else None),
            _stay_point(slept) if slept else (home_pt if last_day else None))


def day_clock(pings, start_pt=None, end_pt=None, radius_m=1000):
    """When the day's travelling actually started and finished, local time.

    The shape of a travel day is not only its distance: leaving the Svendsens'
    at three in the afternoon and leaving at seven in the morning are different
    days, and nothing else in the dossier distinguishes them. AWH pointed at a
    New Year's Day summary that read as a pure driving day when most of it had
    been spent with family before setting off.

    The rule is `_drive_days`': the LAST ping still within `radius_m` of where
    the day started is the departure, and the FIRST ping already within
    `radius_m` of where it ended is the arrival. A campground-sized radius,
    bounding by position rather than by mileage — an evening of GPS jitter at
    camp would otherwise keep the drive "running" for hours.

    **`start_pt` and `end_pt` are the BEDS, and passing them is what makes the
    answer right on a day that begins at home.** The anchors were originally
    the day's first and last PING, which is the same thing only when the phone
    reported from the driveway — and OwnTracks suspends reporting while a
    device sits still, so the first ping of a day that started at home is
    routinely already miles away. On trip 90's 2026-06-05 it was the drive to
    work: the start circle formed around the office, the last ping inside it
    was 07:10, and the dossier reported "left 07:10, arrived 21:11" for a trip
    that left home at 18:54 and drove two hours. The draft duly said "fourteen
    hours between leaving and arriving", and it was the most heavily rewritten
    entry in the library. Where the day started is knowable without the GPS —
    home.json and the trip's own stays — so it is told rather than inferred.
    Falls back to the first/last ping when a bed isn't resolvable.
    """
    if len(pings or []) < 3:
        return {}
    import zoneinfo
    pts = sorted(pings, key=lambda p: p["tst"])
    a = tuple(start_pt) if start_pt else (pts[0]["lat"], pts[0]["lon"])
    b = tuple(end_pt) if end_pt else (pts[-1]["lat"], pts[-1]["lon"])
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
                day_times=None, home_pt=None, contexts=None,
                high_point_ft=None):
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
        elif not item.get("waypoint") and item.get("name"):
            # The TIME matters as much as the name. Without it a bare list in
            # order invites reading the first entry as the morning and a single
            # entry as the whole day — AWH on trip 14's Ocean City: "We didn't
            # spend the day in Ocean City. We spent only a short part of the
            # evening there." It ran 19:30 to 20:47. 98% of non-waypoint events
            # carry a time, so this is nearly always knowable.
            ev = {k: v for k, v in (("name", item["name"]),
                                    ("time", (item.get("time") or "").strip()),
                                    ("until", (item.get("end_time") or "").strip()))
                  if v}
            if ev not in events:
                events.append(ev)
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
        # What the campground SITS in — the water it fronts, the forest or park
        # that contains it. Read off the campground record (`waterfront` is an
        # audited field; the name is pulled from its note), never from the
        # model's own geography. It is the one kind of scene-setting the
        # entries are allowed, and it is not on the timeline card below, so
        # naming it doesn't restate anything the reader is about to read.
        entry.update((contexts or {}).get(slept.get("campground_id")) or {})
        if entry:
            d["to"] = entry

    if high_point_ft:
        # The highest ground the day actually covered, off the DEM. On a day
        # based at one campground the campground's own elevation is the least
        # interesting number available: trip 95's Trail Ridge day was written
        # up as "based at Moraine Park at 8,200 feet" when it was spent near
        # 12,000. Only offered when it clears the beds by enough to be the
        # point (see `day_high_point_ft`).
        d["high_point_ft"] = high_point_ft

    if not d.get("round_trip"):
        # Home is the missing anchor on the day a trip leaves and the day it
        # comes back — `_heading` needs a stay at both ends, and those two days
        # have one. Left absent, the model guesses the compass off the state
        # list, and every wrong heading in the library was one of those days:
        # VA→western PA read "north" (it is northwest), and two runs home from
        # the northwest read "south" (southeast).
        heading = _heading(*day_anchors(trip, day, home_pt, day_index))
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


def _prompt(dossier, examples=()):
    """The dossier as JSON, behind whatever hand-written days resemble it.

    Deliberately not prose: a model handed prose tends to echo its phrasing,
    and the point is for it to write from facts. The examples are the exception
    and they are pairs — the facts a day was written from, then what the family
    wrote about it — so they teach the mapping rather than a vocabulary.

    They ride in the USER message, never in `SYSTEM`: the system block is
    cached across the whole run, and a per-day example bank in it would defeat
    that on every call.
    """
    parts = []
    if examples:
        parts.append(
            "The family's own write-ups for days of a similar shape. They are "
            "the target for length, voice and altitude — match those, not "
            "their wording, and never borrow their places.\n")
        for ex in examples:
            parts.append("FACTS: " + json.dumps(ex["facts"], ensure_ascii=False)
                         + "\nENTRY: " + ex["text"].strip() + "\n")
        parts.append("Now the day to write. Facts:\n")
    else:
        parts.append("Facts for one day. Write the entry.\n")
    parts.append(json.dumps(dossier, indent=2, ensure_ascii=False))
    return "\n".join(parts)


# ── Examples: the family's own days, chosen to match the one being written ──
# These replaced four hand-written exemplars frozen in SYSTEM. Freezing them
# was wrong twice over: the library gained a much better source of truth the
# moment `day_notes` existed (every note is a day AWH wrote AFTER reading what
# the model made of it), and one of the four had by then been superseded — the
# 405-mile exemplar taught "a handful of real stops spaced through it" about a
# day whose own note names all four stops. Selecting at run time means the
# examples can never go stale: writing a note is now the way to correct the
# drafter, and it takes effect on the next run with no prompt edit.
EXAMPLE_COUNT = 4
EXAMPLE_MAX_PER_TRIP = 2


def example_shape(dossier):
    """The few facts example selection matches on."""
    outline = dossier.get("trip_outline") or []
    return {
        "round_trip": bool(dossier.get("round_trip")),
        "miles": dossier.get("miles"),
        "first": dossier.get("day_of_trip") == 1,
        "last": bool(outline) and dossier.get("day_of_trip") == len(outline),
        "events": len(dossier.get("events") or []),
        "family": bool(dossier.get("family_visits")),
    }


def example_score(cand, target):
    """How much like the day being written is this hand-written day?

    Shape, not subject. A day at one campground and a 500-mile haul are
    different kinds of paragraph — one is about what happened and the other
    about the road — so a model shown the wrong kind writes the wrong kind.
    Mileage matters as a ratio rather than a difference: 60 vs 120 miles is a
    real difference in kind, 400 vs 460 is not.
    """
    score = 0.0
    score += 4 if cand["round_trip"] == target["round_trip"] else -4
    if not cand["round_trip"] and not target["round_trip"]:
        a, b = cand.get("miles"), target.get("miles")
        if a and b:
            score += 3 * max(0.0, 1 - abs(math.log(a / b)))
        elif a is None and b is None:
            score += 1
    for flag in ("first", "last", "family"):
        if cand[flag] == target[flag]:
            score += 1.5 if cand[flag] else 0.3
    if (cand["events"] > 0) == (target["events"] > 0):
        score += 1
    score -= 0.2 * abs(cand["events"] - target["events"])
    return score


def choose_examples(bank, dossier, key, count=EXAMPLE_COUNT):
    """The closest hand-written days, capped per trip so one trip's voice
    doesn't become the only voice the model hears."""
    target = example_shape(dossier)
    ranked = sorted(((example_score(e["shape"], target), e) for e in bank
                     if e["key"] != key),
                    key=lambda p: -p[0])
    out, per_trip = [], {}
    for _score, ex in ranked:
        trip_id = ex["key"].split("/")[0]
        if per_trip.get(trip_id, 0) >= EXAMPLE_MAX_PER_TRIP:
            continue
        per_trip[trip_id] = per_trip.get(trip_id, 0) + 1
        out.append(ex)
        if len(out) >= count:
            break
    return out


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
    """Every date the trip covers: the ones its record names, plus the ones the
    PAGE puts a day divider on.

    The two are not the same and each catches what the other drops. The record
    knows the day the trip drove home — a stay's `end` — which carries no
    timeline card at all on a trip that left the morning after its last night.
    The timeline knows the interior days of a split multi-night stay, which the
    record never names anywhere: trip 21's 2023-11-24 has a divider, and a
    write-up slot under it, that nothing was ever drafted for.

    Taking the union is what keeps the drafter and the page agreeing about what
    a day IS. A day on neither list is a day nobody can see.
    """
    days = set()
    for stay in trip.get("stays", []):
        for key in ("start", "end"):
            if stay.get(key):
                days.add(stay[key])
    for evt in trip.get("events", []):
        if evt.get("date"):
            days.add(evt["date"])
    for item in trip.get("timeline", []):
        if item.get("sort_date"):
            days.add(item["sort_date"])
    return sorted(days)


def trip_outline(trip, days, driving, elevations):
    """Every day of the trip in order: how far it went and where it slept.

    `None`, never 0, for a day with no travel distance — unrecorded or round
    trip alike. The same absent-vs-zero trap as the per-day `mileage` field,
    and it bit the same way one fix later: with zeros here the model read trip
    47 as "two days of staying put" when the second of them moved between
    campgrounds.
    """
    def slept_on(d):
        for st in trip.get("stays", []):
            if st.get("start", "") <= d < st.get("end", ""):
                return st
        return None
    out = []
    for n, day in enumerate(days, 1):
        drive = driving.get(day) or {}
        stay = slept_on(day)
        row = {"day": n,
               "miles": None if drive.get("round_trip") else (drive.get("miles") or None),
               "slept": (stay or {}).get("place") or None}
        feet = _elevation_ft(stay, elevations) if stay else None
        if feet:
            row["elevation_ft"] = feet
        out.append(row)
    return out


def _day_dossier_from(trip, day, day_index, pings, driving, outline,
                      elevations, contexts, home_pt, no_elevation=False):
    """One day's dossier, assembled from everything the host can reach.

    The single path to a dossier: the day being drafted and the hand-written
    days used as examples must be described the same way, or the examples teach
    a mapping from facts the model is not given.
    """
    woke = slept = None
    for stay in trip.get("stays", []):
        start, end = stay.get("start", ""), stay.get("end", "")
        if start < day <= end:
            woke = stay
        if start <= day < end:
            slept = stay
    start_pt, end_pt = day_anchors(trip, day, home_pt, day_index)
    beds = [_elevation_ft(s, elevations) for s in (woke, slept) if s]
    high = None if no_elevation else day_high_point_ft(pings, beds)
    return day_dossier(trip, day, driving, elevations, states_crossed(pings),
                       outline, day_index, bool(pings),
                       day_clock(pings, start_pt, end_pt),
                       home_pt, contexts, high)


def build_example_bank(A, trips, elevations, contexts, home_pt,
                       no_elevation=False):
    """Every day somebody wrote a note about, paired with its own dossier.

    `day_notes` is the family's channel and it outranks a draft at display
    time, so a note is nearly always a day where the draft was read and found
    wanting — which makes the pair (facts, what they actually wrote) the best
    training signal in the repo, and one that grows every time a note is typed.

    Read with `get_day_notes`, NOT off the parsed trip: `_make_trip` builds a
    display object and doesn't copy the field, so `trip.get("day_notes")` is
    always empty however many notes exist. That mistake once produced a
    confident "you have no day notes anywhere in the library" while seven sat
    in the file.
    """
    bank = []
    for trip in trips:
        notes = {d: t for d, t in get_day_notes(trip["id"]).items() if (t or "").strip()}
        if not notes:
            continue
        A.enrich_trip_locations(trip)
        driving = A._trip_driving_by_day(trip)
        days = trip_days(trip)
        outline = trip_outline(trip, days, driving, elevations)
        track = _track_by_local_day(A, trip["id"])
        for day_i, day in enumerate(days, 1):
            if day not in notes:
                continue
            dossier = _day_dossier_from(trip, day, (day_i, len(days)),
                                        track.get(day, []), driving, outline,
                                        elevations, contexts, home_pt,
                                        no_elevation)
            # `trip_outline` is dropped from an example: it is the longest
            # field in the dossier and the least transferable — another trip's
            # day-by-day mileage teaches nothing about how to write this one,
            # and four of them would crowd out the day being drafted.
            shape = example_shape(dossier)
            dossier.pop("trip_outline", None)
            bank.append({"key": f"{trip['id']}/{day}", "facts": dossier,
                         "shape": shape, "text": notes[day]})
    return bank


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
    ap.add_argument("--no-elevation", action="store_true",
                    help="skip the DEM lookup for the day's high point "
                         "(offline hosts, or to keep a dry run local)")
    ap.add_argument("--no-examples", action="store_true",
                    help="don't show the model the family's own write-ups "
                         "for similar days")
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()

    _load_dotenv()
    import ekko_trips_app as A

    # One number, owned by the app: the track re-fetch window IS the settle
    # window, and a copy here would drift the day someone tuned it.
    settle_s = getattr(A, "TRACK_REFETCH_OVERLAP_S", SETTLE_AFTER_S)

    all_trips = [t for t in A.parse_trips()
                 if t.get("start") and not t.get("home_only")]
    trips = all_trips
    if args.trip is not None:
        trips = [t for t in trips if t["id"] == args.trip]
        if not trips:
            print(f"no such trip: {args.trip}", file=sys.stderr)
            return 1

    # id -> feet. _load_campgrounds() already converts and is cached; the raw
    # file carries metres and the trimmed locations index carries neither.
    elevations = {c["id"]: c["elevation_feet"] for c in A._load_campgrounds()
                  if c.get("elevation_feet") is not None}
    # id -> what the campground sits in. The `waterfront` half is audited on
    # every entry; the names are parsed from the note (see campground_context).
    contexts = {c["id"]: ctx for c in A._load_campgrounds()
                if (ctx := campground_context(c))}
    try:
        home_pt, _fam = A._map_config()
        home_pt = tuple(home_pt) if home_pt else None
    except Exception:
        home_pt = None
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
        outline = trip_outline(trip, days, driving, elevations)

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
                         _day_dossier_from(trip, day, (day_i, len(days)), pings,
                                           driving, outline, elevations,
                                           contexts, home_pt,
                                           args.no_elevation)))

    if args.limit:
        jobs = jobs[:args.limit]

    # Built once, from the whole library, and only when there is something to
    # write — a run with nothing to draft must still cost nothing.
    bank = []
    if jobs and not args.no_examples:
        # The WHOLE library, never the `--trip` subset: examples are chosen
        # by the shape of a day, and one trip rarely holds four days shaped
        # like the one being written. Drafting a single trip was picking its
        # own two neighbouring days and stopping there.
        bank = build_example_bank(A, all_trips, elevations, contexts, home_pt,
                                  args.no_elevation)
    jobs = [(key, trip, day, sig, dossier,
             choose_examples(bank, dossier, key) if bank else [])
            for key, trip, day, sig, dossier in jobs]
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
        for key, _trip, _day, _sig, dossier, examples in jobs:
            print(f"=== {key} ===")
            print(json.dumps(dossier, indent=2, ensure_ascii=False))
            if examples:
                print("  examples: " + ", ".join(e["key"] for e in examples))
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
    for i, (key, trip, day, sig, dossier, examples) in enumerate(jobs, 1):
        try:
            resp = client.messages.create(
                model=args.model,
                max_tokens=MAX_TOKENS,
                thinking={"type": "adaptive"},
                # The system prompt is identical on every call, so caching it
                # turns 300-odd repeats of it into one.
                system=[{"type": "text", "text": SYSTEM,
                         "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user",
                           "content": _prompt(dossier, examples)}],
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
