#!/usr/bin/env python3
"""Check every drafted day rollup's figures against what the GPS actually measured.

Two questions, because the drafts got both wrong in different ways:

1. IS THE NUMBER REAL? Every mileage figure in an entry must equal the day's
   measured leg or its whole-day total (`trip_routes.json`). A figure matching
   neither is invented, which has never happened -- this is the regression test
   that keeps it that way.

2. IS THE NUMBER IN THE RIGHT PLACE? `miles` in the dossier covers the whole
   day, bed to bed. An entry that names a stop and THEN quotes the figure
   ("Church at Grace Anglican in the morning, then 160 miles east for home")
   reads as a 160-mile run from the church -- when the church was 101 miles
   into a 160-mile day. The figure is right and the sentence is false. This
   measures how far the day had already driven before the first stop the entry
   names, and flags the entry when a meaningful share of the figure fell there.

Read-only; prints findings and exits non-zero if any are found.
"""
import datetime, gzip, json, math, os, re, sys

_DIR = os.path.dirname(os.path.abspath(__file__))
ROLLUPS = os.path.join(_DIR, "trip_data", "day_rollups.json")
ROUTES = os.path.join(_DIR, "trip_data", "trip_routes.json")
TRIPS = os.path.join(_DIR, "trip_data", "trips.json")
TRACKS = os.path.join(_DIR, "trip_data", "track_cache")

MILES = re.compile(r"(\d[\d,]*)\s*(?:-|\s)?miles?\b", re.I)

# Durations come in both orders and the parser must take both: "two and a half
# hours" AND "an hour and a half". Reading only the first form scores the second
# as a bare 1.0 and reports a library of correct entries as rounding down.
_COUNT = r"(?:\d+|an?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
_FRAC = r"(a half|a quarter|three quarters)"
HOURS_PRE = re.compile(rf"\b({_COUNT})\s+and\s+{_FRAC}\s+hours?\b", re.I)
HOURS_POST = re.compile(rf"\b({_COUNT})\s*-?\s*hours?\s+and\s+{_FRAC}\b", re.I)
HOURS_PLAIN = re.compile(rf"\b({_COUNT})\s*-?\s*hours?\b", re.I)
_WORD = {"an": 1, "a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
_FRACV = {"a half": 0.5, "a quarter": 0.25, "three quarters": 0.75}
# An entry may time a STOP rather than the driving ("an hour at George
# Washington Memorial Park", "two hours in the museum"). Those are dwell times
# and answer to nothing here. The marker follows the duration -- "<N> hours at
# <place>" -- so it is the TAIL that has to be read, not the lead-in.
DWELL_TAIL = re.compile(r"^\s*(?:at|in|on|inside|around|exploring|walking)\b", re.I)
# ...but the idioms for DRIVING time start with those same prepositions ("nine
# hours at the wheel", "five hours on the road"). Left unhandled they read as
# dwell and silently exempt the very entries that name a driving duration, so
# they are tested first.
DRIVING_TAIL = re.compile(
    r"^\s*(?:at|behind)\s+the\s+wheel|^\s*on\s+the\s+road|^\s*in\s+the\s+(?:car|saddle|driver)",
    re.I)
HOURS_TOLERANCE_H = 0.42

# Words that place or classify rather than name. Matching on these is what made
# an early version of this check useless: "south" matched "South Seagrove
# Welcome Center" and flagged every entry that opened with a heading.
GENERIC = set("""north south east west northeast northwest southeast southwest rest area stop
plaza service travel center welcome visitor park lake river beach state national forest county
township the of and at on in a an for to gas lunch dinner breakfast brunch morning afternoon
evening night memorial museum trail hike hiking swimming kayaking campsite camp campground place
house home road exxon shell sheetz sunoco wawa citgo marathon walmart wal-mart""".split())

# A stop is "well into the day" once this much of the quoted figure preceded it.
PRE_DRIVE_MIN_MI = 20
PRE_DRIVE_MIN_SHARE = 0.18


def _phrases(name):
    """Distinctive proper-noun phrases from an event name, longest first.

    Every contiguous sub-phrase, because the entry paraphrases: the record says
    "Grace Anglican Church" and the sentence says "Grace Anglican". Requiring
    the full run missed exactly the case this audit was written for.
    """
    runs, run = [], []
    for word in re.findall(r"[A-Za-z'\-]+", name):
        if word.lower() not in GENERIC and len(word) > 3:
            run.append(word)
        else:
            if run:
                runs.append(run)
            run = []
    if run:
        runs.append(run)
    out, seen = [], set()
    for words in runs:
        for n in range(len(words), 0, -1):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i:i + n])
                if phrase.lower() not in seen:
                    seen.add(phrase.lower())
                    out.append(phrase)
    return [p for p in out if " " in p or len(p) >= 7]


def _hours_quoted(text):
    """The entry's driving duration in hours, or None. Returns the match too."""
    for rx in (HOURS_PRE, HOURS_POST):
        m = rx.search(text)
        if m:
            head = m.group(1).lower()
            return (float(head) if head.isdigit() else _WORD.get(head, 0)) + _FRACV[m.group(2).lower()], m
    m = HOURS_PLAIN.search(text)
    if m:
        head = m.group(1).lower()
        return (float(head) if head.isdigit() else _WORD.get(head, 0)), m
    return None, None


def _haversine(a, b):
    R = 6371000
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    x = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(x))


def _path_miles(pings):
    return sum(_haversine((pings[i]["lat"], pings[i]["lon"]),
                          (pings[i + 1]["lat"], pings[i + 1]["lon"]))
               for i in range(len(pings) - 1)) / 1609.34


def _track(trip_id, _cache={}):
    if trip_id not in _cache:
        path = os.path.join(TRACKS, f"{trip_id}.json.gz")
        raw = None
        if os.path.exists(path):
            with gzip.open(path) as fh:
                raw = json.load(fh)
            raw = raw["points"] if isinstance(raw, dict) else raw
        _cache[trip_id] = raw
    return _cache[trip_id]


def _day_pings(points, day):
    """The day's pings. Tries each US offset rather than assuming one -- this is
    an audit, so a day bucketed an hour off would only ever cost a false alarm."""
    for offset in (-4, -5, -6, -7, -8):
        tz = datetime.timezone(datetime.timedelta(hours=offset))
        got = [p for p in points
               if datetime.datetime.fromtimestamp(p["tst"], tz).date().isoformat() == day]
        if got:
            return sorted(got, key=lambda p: p["tst"]), tz
    return [], None


def main():
    rollups = json.load(open(ROLLUPS))
    routes = json.load(open(ROUTES))
    trips = json.load(open(TRIPS))
    trips = {t["id"]: t for t in (trips["trips"] if isinstance(trips, dict) else trips)}

    measured = {}
    for tid, entry in routes.items():
        for day in entry.get("days") or []:
            measured.setdefault((tid, day[0]), {}).update(
                leg=day[1] / 1609.34, elapsed_h=day[2] / 3600, moving_h=day[3] / 3600)
        for day in entry.get("day_totals") or []:
            measured.setdefault((tid, day[0]), {})["total"] = day[1] / 1609.34

    invented, misplaced, durations = [], [], []
    for key, rec in sorted(rollups.items()):
        text = rec.get("text") or ""
        tid, day = key.split("/")

        # Durations, independent of whether the entry also quotes mileage.
        said, hm = _hours_quoted(text)
        ref_h = measured.get((tid, day), {})
        if said and ref_h.get("moving_h"):
            tail = text[hm.end():hm.end() + 30]
            if (DRIVING_TAIL.search(tail) or not DWELL_TAIL.search(tail)) and min(
                    abs(said - ref_h["moving_h"]),
                    abs(said - ref_h.get("elapsed_h", ref_h["moving_h"]))) > HOURS_TOLERANCE_H:
                durations.append((key, said, round(ref_h["moving_h"], 2),
                                  round(ref_h.get("elapsed_h", 0), 2), text))

        match = MILES.search(text)
        if not match:
            continue
        quoted = int(match.group(1).replace(",", ""))

        ref = measured.get((tid, day), {})
        if ref and not any(r and abs(quoted - r) <= max(3, 0.03 * r)
                           for r in (ref.get("leg"), ref.get("total"))):
            invented.append((key, quoted, ref, text))

        events = sorted([e for e in (trips.get(int(tid)) or {}).get("events", [])
                         if e.get("date") == day and e.get("time")],
                        key=lambda e: e["time"])
        low = text.lower()
        named = None
        for event in events:
            for phrase in _phrases(event.get("name", "")):
                at = low.find(phrase.lower())
                if at != -1 and at < match.start():
                    named = event
                    break
            if named:
                break
        if not named:
            continue
        points = _track(int(tid))
        if not points:
            continue
        pings, tz = _day_pings(points, day)
        if not pings:
            continue
        hh, mm = map(int, named["time"].split(":"))
        before = [p for p in pings
                  if (lambda t: t.hour * 60 + t.minute <= hh * 60 + mm)(
                      datetime.datetime.fromtimestamp(p["tst"], tz))]
        pre = _path_miles(before)
        if pre > max(PRE_DRIVE_MIN_MI, PRE_DRIVE_MIN_SHARE * quoted):
            misplaced.append((key, quoted, round(pre), named.get("name"), text))

    if invented:
        print("FIGURES MATCHING NO MEASUREMENT:")
        for key, quoted, ref, text in invented:
            leg = ref.get("leg") and round(ref["leg"])
            total = ref.get("total") and round(ref["total"])
            print(f"  {key}: says {quoted} mi | measured leg {leg}, day {total}")
            print(f"      {text}")
    if misplaced:
        print("FIGURES HUNG ON THE WRONG LEG (the day had already driven this far):")
        for key, quoted, pre, name, text in misplaced:
            print(f"  {key}: says {quoted} mi after \"{name}\" | {pre} mi came before it")
            print(f"      {text}")
    if durations:
        print("DURATIONS MATCHING NEITHER DRIVING TIME NOR ELAPSED SPAN:")
        for key, said, moving, elapsed, text in durations:
            print(f"  {key}: says {said}h | driving {moving}h, elapsed {elapsed}h")
            print(f"      {text}")
    if not invented and not misplaced and not durations:
        print(f"clean: {len(rollups)} rollups, every mileage and duration figure "
              "real and correctly placed")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
