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
import sys
import time
from datetime import date as _date

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

ROLLUPS_FILE = os.path.join(_DIR, "trip_data", "day_rollups.json")
MEMOS_FILE = os.path.join(_DIR, "trip_data", "memos.json")

MODEL = "claude-opus-5"

# Short on purpose. The failure mode is padding: given four facts and room for
# three hundred words, a model reaches for atmosphere. A tight ceiling makes
# "not much happened" an available answer.
MAX_TOKENS = 700

SYSTEM = """You write one short diary entry for one day of a family's camping trip, \
from a dossier of facts.

RULES, in order of importance:

1. Every statement must come from the dossier. If it is not in there, it did \
not happen. Never invent weather, scenery, feelings, motives, or reactions. \
"They enjoyed the view" is a fabrication unless someone said so.
2. If the day holds little, write little. Two sentences is a complete entry for \
a day that was mostly driving. Do not pad.
3. Quoted memos are the family speaking. Prefer what they said over the \
statistics. Attribute by name when a memo names its speaker and the day has \
more than one — otherwise just say what was said.
4. Plain past tense, first person plural ("we"), the way someone writes up \
their own day. No brochure language: nothing is nestled, stunning, breathtaking, \
scenic or a hidden gem.
5. Do not restate the date, the trip name, or the day number — the page already \
shows them. Do not use headings or bullet points. Prose only.
6. "unremarkable_stops" is a count of gas stations and rest areas, kept \
deliberately nameless. Mention it only if the day is otherwise thin, and never \
name or characterise them.
7. Numbers stay as given. Do not round 520 miles to "over 500" or convert units.

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


def day_dossier(trip, day, driving, locations, memos, photo_counts,
                card_photos=None):
    """Everything known about one day of one trip, as a plain dict.

    This is the half worth getting right. The model can only be as honest as
    its input, and an empty dossier is what produces invented atmosphere — so
    anything genuinely unknown is simply absent rather than guessed at.
    """
    d = {"date": day, "weekday": "", "trip": trip.get("summary", ""),
         "stops": [], "memos": [], "photos": photo_counts.get(day, 0)}
    try:
        d["weekday"] = _date.fromisoformat(day).strftime("%A")
    except ValueError:
        pass

    drive = driving.get(day) or {}
    if drive.get("miles"):
        d["driving"] = {
            "miles": drive["miles"],
            "time": drive.get("moving") or "",
            "round_trip": bool(drive.get("round_trip")),
        }

    # Where we slept, and what the campground record knows about it. The
    # curated `note` is the owner's own words about the place and is often the
    # most human thing available on a day with no memos.
    for stay in trip.get("stays", []):
        if not (stay.get("start", "") <= day <= stay.get("end", "")):
            continue
        night = {"place": stay.get("place", ""),
                 "where": ", ".join(x for x in (stay.get("locale"), stay.get("state")) if x),
                 "arriving": stay.get("start") == day,
                 "leaving": stay.get("end") == day}
        for key in ("site", "campers", "notes"):
            if stay.get(key):
                night[key] = stay[key]
        cg = locations.get(stay.get("campground_id"))
        if cg:
            for src, dst in (("elevation_meters", "elevation_m"),
                             ("waterfront", "waterfront"),
                             ("ownership", "ownership"), ("note", "campground_note")):
                if cg.get(src) and cg.get(src) != "not waterfront":
                    night[dst] = cg[src]
        d.setdefault("nights", []).append(night)

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
    card_photos = card_photos or {}
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
                "where": ", ".join(x for x in (evt.get("locale"), evt.get("state")) if x)}
        if evt.get("waypoint"):
            stop["brief"] = True
        if card_photos.get(f"event-{i}"):
            stop["photos"] = card_photos[f"event-{i}"]
        for key, out in (("time", "time"), ("end_time", "until"),
                         ("description", "description"), ("family_visit", "visiting")):
            if evt.get(key):
                stop[out] = _fmt_time(evt[key]) if "time" in key else evt[key]
        d["stops"].append(stop)
    d["stops"].sort(key=lambda s: s.get("time", "99:99"))
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
        counts, per_card = {}, {}
        for p in pool:
            if p["trip_id"] != trip["id"]:
                continue
            per_card[p["card"]] = per_card.get(p["card"], 0) + 1
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
                                     counts, per_card)))

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
            print(f"  {key}: refused", file=sys.stderr)
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
