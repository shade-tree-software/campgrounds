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

SYSTEM = """You write one short diary entry for one day of a family's camping trip, \
from a dossier of facts.

RULES, in order of importance:

1. Every statement must come from the dossier. If it is not in there, it did \
not happen. Never invent weather, scenery, feelings, motives, or reactions. \
"They enjoyed the view" is a fabrication unless someone said so.
2. THE INVENTION IS ALWAYS IN THE JOINS. Rule 1 is easy to keep for whole \
facts and almost impossible to keep while making sentences flow, because \
fluent prose wants a preposition, a motive, a mood — and those are exactly what \
the dossier does not have. Every one of the following was written from a source \
that did not say it:
   WHERE, relative to something else. "We talked briefly to a group of men on \
Harleys" became "at the top we talked to them"; they were in the car park. \
"A quick stop at the park sign" became "on the way back through town"; there is \
no town within miles of it.
   HOW NEARLY something was missed, or any other counterfactual. "We would have \
missed it were it not for her research" became "we'd have driven right past it" \
— a specific claim about a road nobody mentioned.
   WHY a stop took as long as it did. A seventy-minute stop labelled "breakfast" \
is not a seventy-minute breakfast; it is a stop at which breakfast happened.
   THE MOOD OF THE DAY. "After the day we'd had" turned a long day into a bad \
one. Length is in the dossier; disappointment, relief and exhaustion are not.
   WHOSE IDEA something was, WHO NAMED something, and WHAT ANYTHING WAS FOR. \
"One more stop" does not become "a stop for the car".
   If you cannot say something without inventing the join, say the smaller true \
thing, or leave it out. An entry that omits a detail is fine. An entry that \
invents one is not.
3. If the day holds little, write little. Two sentences is a complete entry for \
a day that was mostly driving. Do not pad.
4. THE FAMILY'S OWN WORDS ARE THE SUBSTANCE OF THE ENTRY, and the facts are \
the scaffolding around them. Two fields carry those words — "photo_captions" \
(written on their own photographs) and the "notes" on a place they stayed. \
Prefer both to any statistic, and let them decide what the day was about.
   FOLD THEM IN; DO NOT QUOTE THEM. Rewrite what was written in the same voice \
as the rest of the entry, in its place in the day, so a reader cannot tell \
which sentence began as a caption and which as a fact. One dropped in between \
quotation marks reads as a clipping pasted into a diary, and it strands the \
prose on either side of it. The same goes for announcing the source: never \
"one photo is captioned" or "the note says".
   FOLDING IS REWRITING, NOT SUMMARISING. Every specific thing written must \
survive — the horizon-to-horizon view, the woman at the corn stand, the last \
week of the season. Losing a detail to make a sentence flow is a worse failure \
than an ungainly sentence. Add nothing that was not written.
   What someone wrote may be the frame for the whole day rather than a line \
inside it. If it IS the day, build the entry around it and let the stops fall \
in behind.
   Name a person only when what was written is about them or belongs to them \
("Donna had read that Lily Lake was a must-see"). Otherwise the family speaks \
as "we", like the rest of the entry — a name on every sentence is just \
attribution noise.
   A phrase may stay verbatim when it is the whole point of the sentence and \
paraphrase would flatten it — an aside like "we still don't know why the town \
has a lit Christmas tree in August" survives because the wording is the joke. \
That is a rare exception, not the default.
5. Plain past tense, first person plural ("we"), the way someone writes up \
their own day. No brochure language: nothing is nestled, stunning, breathtaking, \
scenic or a hidden gem.
6. Do not restate the date, the trip name, or the day number — the page already \
shows them. Do not use headings or bullet points. Prose only.
7. "unremarkable_stops" is a count of gas stations and rest areas, kept \
deliberately nameless. Mention it only if the day is otherwise thin, and never \
name or characterise them.
8. Photo counts tell you which stops mattered most — the family photographed \
them. Use them to decide what to write about. NEVER state or allude to one. \
Not "fourteen photos for the day", and equally not "where we took most of the \
day's pictures" or "more of our film than anything else" — a comparison is \
still a fact about the archive rather than about the day.
9. Do not list who was there. The names are on the page already, and a day \
reads as an inventory when it ends in a roll call. Name someone only when \
something is said about them.
10. "driving" is how the day FELT, not a figure to quote. Say it was a long day \
if it is worth saying; the exact mileage and hours are printed beside your entry \
already. A day with no "driving" key does not need its travel mentioned at all.
11. Times order the day; they are not for reciting. "time"/"until" tell you what \
came first and how long it took, so write "the afternoon went to" or "an hour or \
so at" — never "from a quarter to nine until nearly four".
12. Say where something is only when the dossier gives a "where". A stop with \
none is out in the country, and the honest thing is to name the stop and stop \
there. Never invent a town, county, or region for it.
13. Never invent HOW a place was experienced. Walked, drove, hiked, toured, \
climbed, paddled, ate — unless the dossier says which, the verb is "went to", \
"stopped at" or "spent time at". Writing "we drove Snake Alley" about a street \
the dossier only calls the crookedest in the world is a fabrication, and it is \
wrong: they walked it.
14. A CAPTION IS A LABEL ON A PHOTOGRAPH YOU CANNOT SEE, and most of what it \
means is in the picture. "That's the moon" identifies something in a frame. \
"Not in service" is about an object in one — an abandoned phone booth, as it \
happens, not the town it stands in. "Munchkinland" turned out to be a sign on a \
playground, not what the family called the place.
   So: use a caption only when it stands ON ITS OWN as a statement about the \
day, the way "Donna says prairie dogs are vicious" and "Idaho Springs claims to \
be where the Gold Rush started" do. If understanding it requires seeing the \
photograph, leave it out — a caption you cannot place is not a fact you have. \
Never guess its subject, never guess who wrote or said it, and never rebuild it \
into an action the family took.
   Captions are often jokes, and a joke reported as a fact is worse than a joke \
left out: "Wait, they have trees in Nebraska?" is an aside about a photograph, \
not a question the family set out to answer.
15. A NAME IS A NAME, NOT A DESCRIPTION. "Sinclair (dinosaur) gas" is a \
parenthetical telling the family which chain it was — every Sinclair sign \
carries that dinosaur — not a distinguishing feature of that one station. Do \
not unpack a name into prose about what the place is like.
16. They travel in a 23-foot camper, and it is a camper or the RV — never a \
car. "A stop for the car" is wrong twice over: wrong vehicle, and an invented \
reason for a stop the dossier only counted.
17. A stop's own times bound how big it may sound. Forty-five minutes is "a \
stop" or "three quarters of an hour", never "we spent the afternoon". Do not \
inflate a short visit into a long one to give a thin day more weight.

Return only the entry text."""


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


def day_dossier(trip, day, driving, locations, photo_counts,
                card_photos=None, card_captions=None):
    """Everything known about one day of one trip, as a plain dict.

    This is the half worth getting right. The model can only be as honest as
    its input, and an empty dossier is what produces invented atmosphere — so
    anything genuinely unknown is simply absent rather than guessed at.
    """
    card_photos = card_photos or {}
    # What was written ON the photos. Captions are the second-most human thing
    # in the archive — "Just like the Bruce Springsteen album
    # cover", "No mountains yet" — and the dossier used to carry only photo
    # COUNTS, so every one of them was invisible to the rollups.
    card_captions = card_captions or {}
    d = {"date": day, "weekday": "", "trip": trip.get("summary", ""),
         "stops": [], "photos": photo_counts.get(day, 0)}
    try:
        d["weekday"] = _date.fromisoformat(day).strftime("%A")
    except ValueError:
        pass

    bucket = _drive_bucket(driving.get(day))
    if bucket:
        d["driving"] = bucket

    # Where we slept, named as the two different facts they are.
    #
    # One `nights` list matched with `start <= day <= end` conflated them: on a
    # departure day it handed over the night BEFORE, flagged `leaving: true`,
    # and said nothing about where the day ended. On the last day of a trip
    # that is every fact the model has, so trip 95's 1 September came out as
    # "that night was our last at Bulltown Campground" — they had left Bulltown
    # that morning and driven 243 miles home. Every trip's final day had it.
    for stay_idx, stay in enumerate(trip.get("stays", [])):
        start, end = stay.get("start", ""), stay.get("end", "")
        tonight = start <= day < end          # we sleep here
        last_night = start < day <= end       # we woke here
        if not (tonight or last_night):
            continue
        night = {"place": stay.get("place", ""),
                 "where": _where(stay.get("where_label") or stay.get("locale"),
                                 stay.get("state"))}
        if not night["where"]:
            night.pop("where")
        if stay.get("site"):
            night["site"] = stay["site"]
        # Captions belong to the day you pull in, exactly as the place's own
        # description does. A stay appears on two days — as `sleeping_at` and
        # again as `woke_up_at` — and each day is drafted by a SEPARATE call
        # with no knowledge of the others, so anything present on both is
        # guaranteed to be said twice. "Donna says prairie dogs are vicious"
        # duly turned up on the 28th and again on the 29th.
        if start == day and card_captions.get(f"stay-{stay_idx}"):
            night["photo_captions"] = card_captions[f"stay-{stay_idx}"]
        # The place's own description belongs to the day you PULL IN. Attached
        # to every day of a stay it gets recited on each of them — trip 95 told
        # us about Prophetstown's prairie grass on both the 20th and the 21st,
        # and Moraine Park's elevation three days running.
        if start == day:
            if stay.get("notes"):
                night["notes"] = stay["notes"]
            cg = locations.get(stay.get("campground_id"))
            if cg:
                for src, dst in (("elevation_meters", "elevation_m"),
                                 ("waterfront", "waterfront"),
                                 ("ownership", "ownership"),
                                 ("note", "campground_note")):
                    val = cg.get(src)
                    if val and not (src == "waterfront" and val == "not waterfront"):
                        night[dst] = val
        if tonight:
            d["sleeping_at"] = night
        else:
            d["woke_up_at"] = night
    if "sleeping_at" not in d and d.get("woke_up_at"):
        d["ended"] = "home — the last day of the trip"

    # What we stopped at — applying the SAME test the timeline applies.
    #
    # Detect Stops is generous: two thirds of the library's events are
    # waypoints, and a travel day's list is mostly gas stations and rest areas
    # (trip 95's 20 August: Amoco, I-70 West Rest Area, South Vienna Rest
    # Area...). Handing those to a writer is how you get a paragraph about
    # buying fuel. A waypoint earns a mention exactly as it earns a card — by
    # having photos or a description — and the rest become a count, so the day
    # can still say four stops were made without naming any of them.
    #
    # Keeping the two rules identical also keeps the page honest: a rollup
    # should not describe something the timeline above it has folded away.
    ref_tz = reference_timezone(trip.get("events"))
    brief = 0
    for i, evt in enumerate(trip.get("events", [])):
        if evt.get("date") != day:
            continue
        earned = (not evt.get("waypoint")
                  or (evt.get("description") or "").strip()
                  or card_photos.get(f"event-{i}"))
        if not earned:
            brief += 1
            continue
        stop = {"name": evt.get("name", ""),
                "where": _where(evt.get("where_label") or evt.get("locale"),
                                evt.get("state"))}
        if not stop["where"]:
            stop.pop("where")
        if evt.get("waypoint"):
            stop["brief"] = True
        if card_photos.get(f"event-{i}"):
            stop["photos"] = card_photos[f"event-{i}"]
        if card_captions.get(f"event-{i}"):
            stop["photo_captions"] = card_captions[f"event-{i}"]
        for key, out in (("time", "time"), ("end_time", "until"),
                         ("description", "description"), ("family_visit", "visiting")):
            if evt.get(key):
                stop[out] = _fmt_time(evt[key]) if "time" in key else evt[key]
        stop["_rank"] = event_time_rank(day, evt.get("time"), evt.get("tz"), ref_tz)
        d["stops"].append(stop)
    # By true instant, not by wall clock. A trip that crosses a time-zone line
    # westward sets the clock BACK, so a later stop wears an earlier stamp:
    # trip 95's Macklin Bay (08:47 CDT) really precedes the Benkelman gas stop
    # (08:35 MDT) by 44 minutes, and a naive sort on "time" hands the model the
    # two backwards. `trips.event_time_rank` is the app's single definition of
    # what happened first, shared with storage order, the timeline, the route
    # anchor walk and the detail map; this is the fifth consumer.
    d["stops"].sort(key=lambda s: s["_rank"])
    for stop in d["stops"]:
        del stop["_rank"]
    if brief:
        d["unremarkable_stops"] = brief

    return d


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
    from trips import _load_locations_by_id

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

    locations = _load_locations_by_id()
    rollups = _load(ROLLUPS_FILE)

    # Photos per day, via the card each photo hangs off.
    pool = A._collect_photo_pool()

    jobs = []
    held = 0
    stamps = {}
    for trip in trips:
        A.enrich_trip_locations(trip)
        driving = A._trip_driving_by_day(trip)
        card_day = {}
        for item in trip.get("timeline", []):
            card = (f"stay-{item['idx']}" if item["type"] == "stay"
                    else f"event-{item['idx']}")
            card_day.setdefault(card, item.get("sort_date"))
        counts, per_card, per_card_caps = {}, {}, {}
        for p in pool:
            if p["trip_id"] != trip["id"]:
                continue
            per_card[p["card"]] = per_card.get(p["card"], 0) + 1
            caption = (p.get("caption") or "").strip()
            if caption:
                per_card_caps.setdefault(p["card"], []).append(caption)
            day = card_day.get(p["card"])
            if day:
                counts[day] = counts.get(day, 0) + 1

        for day in trip_days(trip):
            key = f"{trip['id']}/{day}"
            existing = rollups.get(key) or {}
            # `edited` is a human correcting a draft; `source: conversation`
            # is a human having written the whole thing (trip 95's set, which
            # is also the voice the prompt is calibrated against). Both outrank
            # --force for the same reason, and only --force-edited passes.
            human = existing.get("edited") or existing.get("source") == "conversation"
            if human and not args.force_edited:
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
            jobs.append((key, trip, day, sig,
                         day_dossier(trip, day, driving, locations,
                                     counts, per_card, per_card_caps)))

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
