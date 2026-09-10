#!/usr/bin/env python3
"""Draft a short write-up for each day of a trip.

Step 3 of the memo-to-rollup pipeline, and the first part of it whose output is
a judgement call rather than a verifiable answer. Steps 1 and 2 file voice
memos against the right day and turn them into text; this assembles everything
known about a day — the GPS, the campground, the photos, and whatever was said
into the phone — and asks Claude for a few sentences.

    python process_rollups.py --trip 95 --dry-run   # see the facts, no API call
    python process_rollups.py --trip 95             # draft one trip
    python process_rollups.py                       # draft every day missing one
    python process_rollups.py --force --trip 95     # redo (keeps hand edits)

**Start with --dry-run.** It prints the dossier each day would be written from
and costs nothing. Garbage in is confabulation out, so the dossier is the half
worth checking first; the prose is easy to judge and cheap to redo.

**A day with no memos still gets an entry**, written from facts alone — the
GPS knows the route, the mileage and the stops, and the campground record knows
where you slept. That is deliberate: memos should make a day better, not decide
whether it gets written at all, and it is what lets the whole back catalogue be
covered before a single new memo exists.

**The constraint against invention is the point of this script.** A model handed
facts will write fluent prose and will also invent connective tissue — the
crisp mountain air, the sense of relief — that reads fine today and is
unfalsifiable in twenty years. The system prompt forbids it, the dossier gives
nothing to embroider, and every rollup is stamped with the model that wrote it
so a generated sentence is never mistaken for something you said.

**A hand-edited rollup is never overwritten**, not even by --force; the app sets
`edited` when you fix one. Same rule as memo transcripts, for the same reason.

Needs: pip install -r tools_requirements.txt, and ANTHROPIC_API_KEY in the
environment or in the repo's gitignored .env.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import date as _date

from trips import event_time_rank, reference_timezone

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

ROLLUPS_FILE = os.path.join(_DIR, "trip_data", "day_rollups.json")
MEMOS_FILE = os.path.join(_DIR, "trip_data", "memos.json")

MODEL = "claude-opus-5"

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
2. If the day holds little, write little. Two sentences is a complete entry for \
a day that was mostly driving. Do not pad.
3. THE FAMILY'S OWN WORDS ARE THE SUBSTANCE OF THE ENTRY, and the facts are \
the scaffolding around them. Three fields carry those words — "memos" (spoken \
or typed into a phone), "photo_captions" (written on their own photographs) and \
the "notes" on a place they stayed. Prefer all three to any statistic, and let \
them decide what the day was about.
   FOLD THEM IN; DO NOT QUOTE THEM. Rewrite what was said in the same voice as \
the rest of the entry, in its place in the day, so a reader cannot tell which \
sentence began as a memo and which as a fact. A memo dropped in between \
quotation marks reads as a transcript pasted into a diary, and it strands the \
prose on either side of it. The same goes for announcing the source: never \
"a memo says", "Andrew noted", or "one photo is captioned".
   FOLDING IS REWRITING, NOT SUMMARISING. Every specific thing said must \
survive — the horizon-to-horizon view, the woman at the corn stand, the last \
week of the season. Losing a detail to make a sentence flow is a worse failure \
than an ungainly sentence. Add nothing that was not said.
   A memo may be the frame for the whole day rather than a line inside it. If \
what someone said IS the day, build the entry around it and let the stops fall \
in behind.
   Name a person only when what was said is about them or belongs to them \
("Donna had read that Lily Lake was a must-see"). Otherwise the family speaks \
as "we", like the rest of the entry — a speaker's name on every sentence is \
just attribution noise. In particular do not turn a memo into a quotation with \
the speaker attached: "Andrew decided Nebraska might be the opposite of \
Northern Virginia" is the seam this rule exists to remove. It was simply the \
opposite of Northern Virginia, and "we" saw it.
   A phrase may stay verbatim when it is the whole point of the sentence and \
paraphrase would flatten it — an aside like "we still don't know why the town \
has a lit Christmas tree in August" survives because the wording is the joke. \
That is a rare exception, not the default.
4. Plain past tense, first person plural ("we"), the way someone writes up \
their own day. No brochure language: nothing is nestled, stunning, breathtaking, \
scenic or a hidden gem.
5. Do not restate the date, the trip name, or the day number — the page already \
shows them. Do not use headings or bullet points. Prose only.
6. "unremarkable_stops" is a count of gas stations and rest areas, kept \
deliberately nameless. Mention it only if the day is otherwise thin, and never \
name or characterise them.
7. Photo counts tell you which stops mattered most — the family photographed \
them. Use them to decide what to write about. NEVER state or allude to one. \
Not "fourteen photos for the day", and equally not "where we took most of the \
day's pictures" or "more of our film than anything else" — a comparison is \
still a fact about the archive rather than about the day.
8. Do not list who was there. The names are on the page already, and a day \
reads as an inventory when it ends in a roll call. Name someone only when \
something is said about them.
9. "driving" is how the day FELT, not a figure to quote. Say it was a long day \
if it is worth saying; the exact mileage and hours are printed beside your entry \
already. A day with no "driving" key does not need its travel mentioned at all.
10. Times order the day; they are not for reciting. "time"/"until" tell you what \
came first and how long it took, so write "the afternoon went to" or "an hour or \
so at" — never "from a quarter to nine until nearly four".
11. Say where something is only when the dossier gives a "where". A stop with \
none is out in the country, and the honest thing is to name the stop and stop \
there. Never invent a town, county, or region for it.
12. Never invent HOW a place was experienced. Walked, drove, hiked, toured, \
climbed, paddled, ate — unless the dossier says which, the verb is "went to", \
"stopped at" or "spent time at". Writing "we drove Snake Alley" about a street \
the dossier only calls the crookedest in the world is a fabrication, and it is \
wrong: they walked it.
13. A caption is often the only reason a stop is worth a sentence at all — it \
is what the family thought worth saying about a photograph they chose to keep. \
Fold it in as rule 3 requires.
14. A stop's own times bound how big it may sound. Forty-five minutes is "a \
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

    Same contract as process_memos.py: the app edits this file (a hand
    correction sets `edited`), so a long batch must not dump a stale snapshot
    over the top of an edit made while it ran.
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


def day_dossier(trip, day, driving, locations, memos, photo_counts,
                card_photos=None, card_captions=None):
    """Everything known about one day of one trip, as a plain dict.

    This is the half worth getting right. The model can only be as honest as
    its input, and an empty dossier is what produces invented atmosphere — so
    anything genuinely unknown is simply absent rather than guessed at.
    """
    card_photos = card_photos or {}
    # What was written ON the photos. Captions are the second-most human thing
    # in the archive after the memos — "Just like the Bruce Springsteen album
    # cover", "No mountains yet" — and the dossier used to carry only photo
    # COUNTS, so every one of them was invisible to the rollups.
    card_captions = card_captions or {}
    d = {"date": day, "weekday": "", "trip": trip.get("summary", ""),
         "stops": [], "memos": [], "photos": photo_counts.get(day, 0)}
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

    for rec in memos.values():
        if rec.get("trip_id") != trip["id"] or rec.get("date") != day:
            continue
        text = (rec.get("transcript") or "").strip()
        if not text:
            continue
        d["memos"].append({"said_by": rec.get("speaker") or "", "said": text,
                           "at": rec.get("place", "")})
    return d


def _prompt(dossier):
    """The dossier as JSON. Deliberately not prose: a model handed prose tends
    to echo its phrasing, and the point is for it to write from facts."""
    return ("Facts for one day. Write the entry.\n\n"
            + json.dumps(dossier, indent=2, ensure_ascii=False))


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
    ap.add_argument("--limit", type=int, help="stop after this many days")
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()

    _load_dotenv()
    import ekko_trips_app as A
    from trips import _load_locations_by_id

    trips = [t for t in A.parse_trips()
             if t.get("start") and not t.get("home_only")]
    if args.trip is not None:
        trips = [t for t in trips if t["id"] == args.trip]
        if not trips:
            print(f"no such trip: {args.trip}", file=sys.stderr)
            return 1

    locations = _load_locations_by_id()
    memos = _load(MEMOS_FILE)
    rollups = _load(ROLLUPS_FILE)

    # Photos per day, via the card each photo hangs off.
    pool = A._collect_photo_pool()

    jobs = []
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
            if existing.get("edited") and not args.force_edited:
                continue
            if existing.get("text") and not (args.force or args.force_edited):
                continue
            jobs.append((key, trip, day,
                         day_dossier(trip, day, driving, locations, memos,
                                     counts, per_card, per_card_caps)))

    if args.limit:
        jobs = jobs[:args.limit]
    if not jobs:
        print("Nothing to draft — every day already has a rollup.")
        return 0
    print(f"{len(jobs)} day(s) to draft.\n")

    if args.dry_run:
        for key, _trip, _day, dossier in jobs:
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
    for i, (key, trip, day, dossier) in enumerate(jobs, 1):
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
            "source_memo_ids": [m for m, r in memos.items()
                                if r.get("trip_id") == trip["id"]
                                and r.get("date") == day],
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
