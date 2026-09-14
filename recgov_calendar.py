#!/usr/bin/env python3
"""Derive season (and a first-come signal) for federal campgrounds from the
recreation.gov availability calendar, without anyone reading an agency page.

docs/campground-schema.md §7 phase 4. 2,283 entries carry a
`/camping/campgrounds/<id>` link, and the calendar answers per FACILITY — which
is the resolution federal policy actually varies at, and the reason the
`federal` registry row is deliberately thin. Nothing here needs an API key: the
availability endpoint is a keyless sibling of RIDB (see `ridb/fetch_facility`).

Dry-run by default. `--apply` backs up campgrounds.json first.

**What the calendar can and cannot say.** Five statuses appear:

    Available / Reserved / Open   the site is in service that night — OPEN
    Not Reservable                not bookable that night
    NYR                           "not yet released" — NO INFORMATION

`Reserved` counts as open: somebody is camping there, which is the strongest
possible evidence the campground was in service. `NYR` is the trap — it looks
like a closure and means only that the booking window has not reached that date
yet, so treating it as closed would report every campground as shutting exactly
six months out. A day is closed only when every site says `Not Reservable` and
something was actually returned.

**A whole month of `Not Reservable` is a closure; a few sites are not.** Hirz
Bay reads `Not Reservable` across all 47 sites from October through April and is
plainly shut for the winter. But mid-season the same status on SOME sites while
others are bookable is ambiguous — a walk-up loop, a maintenance closure, or a
group area — so `--fcfs` reports that signal and never writes it.

**FCFS is NOT derivable from this API, and that is a finding rather than a gap.**
A genuinely walk-up campground has nothing to reserve, so it returns either no
campsites or `Not Reservable` on every date — which is byte-identical to a
campground shut for the season. The two cannot be told apart from the calendar
alone, and measured across the first facilities walked the open-day share sat at
0.99-1.00 with no separation to threshold on. `--fcfs` prints the distribution
so the negative result stays visible; it must not be promoted into a written
field. The registry's `federal` row withholding `fcfs` remains the honest state.

**The window is rolling and roughly annual**, about three months back to eight
forward (checked 2026-09: May 2026 is a 400, June 2026 through May 2027 answer).
Months outside it return HTTP 400, which is not an error to report. That means a
single run usually sees a full year — but not always the same year, so
observations ACCUMULATE in `trip_data/recgov_calendar.json` (gitignored,
regenerable) and the season is re-derived from everything ever seen. A run in
spring fills the opening edge a run in autumn could not reach.

**Yield is partial by construction, and accrues.** A facility only publishes
dates inside its own booking window, so one run typically observes ~120 days of
the year, not 365 — enough to catch an edge that happens to fall in the window,
not enough to bound a season. Of the first ten facilities walked, one confirmed
year-round and one a closing date; the other eight honestly returned nothing.
That is the expected shape: run it every couple of months and the cache fills in
edges the previous run could not reach.

The walk is one request per facility per month, so ~12 per campground and
~27,000 for the whole federal set — a multi-day unattended job, not a session's
work. It is resumable by design: the cache is written after every facility,
`--limit` does a batch, a re-run skips everything already held, and
`--max-age-days` refreshes stale ones.
"""

import argparse
import calendar
import datetime
import json
import os
import re
import shutil
import sys
import time
import urllib.error
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import campground_schema
from ridb.fetch_facility import fetch_availability_month

CAMPGROUNDS_JSON = "campgrounds.json"
CACHE_JSON = os.path.join("trip_data", "recgov_calendar.json")

FACILITY_URL = re.compile(r'recreation\.gov/camping/campgrounds/(\d+)')

# A site is in service that night. "Reserved" is the strongest signal of all:
# somebody is camping there.
OPEN_STATUSES = {"Available", "Reserved", "Open"}
CLOSED_STATUS = "Not Reservable"
# "Not yet released" — the booking window simply has not reached this date.
# Counting it as closed would report every campground shutting six months out.
UNKNOWN_STATUSES = {"NYR"}

OPEN, CLOSED, UNKNOWN = "o", "c", "?"

# A season EDGE is only real when an open day and a closed day sit next to each
# other on the calendar. Allow a couple of days of slack so one odd day inside a
# gap doesn't hide a genuine transition, but no more — a two-month hole between
# the last open day and the first closed one places the edge nowhere.
EDGE_MAX_GAP_DAYS = 3
# Claiming YEAR-ROUND needs near-complete coverage, because it is a claim about
# every day including the ones not observed. An edge needs none: it is a claim
# about two adjacent days that were.
MIN_DAYS_FOR_YEAR_ROUND = 300
# A seasonal closure runs for MONTHS. A run of a day or three is a maintenance
# closure, a flooded loop, or one night the whole campground happened to be out
# of service — and read as a season boundary it produces nonsense: Dennis Cove
# yielded "opens 09-11, closes 09-09" off a single closed day, and Backbone Rock
# four edges inside ten days. Runs shorter than this are erased before any edge
# is computed, in both directions.
MIN_RUN_DAYS = 14
# Allow a handful of odd days inside a season (a closed loop, a storm) without
# splitting it into two.
YEAR_ROUND_CLOSED_TOLERANCE = 0.02


def facility_ids(entries):
    """{campground id: facility id} for entries the calendar can answer for."""
    out = {}
    for entry in entries:
        found = FACILITY_URL.findall(entry.get("website") or "")
        if not found:
            continue
        # Two entries cite more than one facility; the first link is the
        # campground's own page in every case checked.
        out[entry["id"]] = found[0]
    return out


def month_string(avail, year, month):
    """One character per day of the month: open, closed, or unknown."""
    days = calendar.monthrange(year, month)[1]
    per_day = [Counter() for _ in range(days)]
    for statuses in avail.values():
        for key, status in statuses.items():
            try:
                day = int(key[8:10])
            except (ValueError, IndexError):
                continue
            if 1 <= day <= days:
                per_day[day - 1][status] += 1
    out = []
    for counts in per_day:
        if any(s in OPEN_STATUSES for s in counts):
            out.append(OPEN)
        elif counts.get(CLOSED_STATUS) and not (set(counts) - {CLOSED_STATUS}):
            out.append(CLOSED)
        else:
            out.append(UNKNOWN)      # all NYR, or nothing returned at all
    return "".join(out)


class RateLimited(RuntimeError):
    """The endpoint is shedding load. Stop; do not record absences."""


def walk_months(fid, months, cache_entry, pause=1.0, backoff=(60, 180, 420)):
    """Fetch each (year, month) not already cached. Returns how many were hit."""
    fetched = 0
    for year, month in months:
        key = f"{year:04d}-{month:02d}"
        if key in cache_entry.get("months", {}):
            continue
        try:
            avail = fetch_availability_month(fid, year, month, cache=None)
        except urllib.error.HTTPError as exc:
            if exc.code == 400:
                continue     # outside the rolling window — expected, not an error
            if exc.code == 429:
                # MUST NOT be swallowed. A rate-limited fetch recorded as an
                # empty month is indistinguishable from a campground that
                # genuinely publishes no calendar — forever, and silently. The
                # first version of this script did exactly that and reported 19
                # of 30 facilities as having "no calendar data at all".
                #
                # Backing off in MINUTES rather than seconds is what makes an
                # unattended multi-hour run possible: the limiter punishes a
                # burst for a long while afterwards, so a fast retry just
                # re-triggers it. A short pause is not a substitute — 0.25s drew
                # 429s within 30 facilities and 1.2s still did, because the
                # earlier burst was still being held against the caller.
                if backoff is None:
                    raise RateLimited(f"facility {fid} {key}: HTTP 429") from exc
                for wait in backoff:
                    print(f"    429 — backing off {wait}s", flush=True)
                    time.sleep(wait)
                    try:
                        avail = fetch_availability_month(fid, year, month,
                                                         cache=None)
                        break
                    except urllib.error.HTTPError as retry_exc:
                        if retry_exc.code == 400:
                            avail = None
                            break
                        if retry_exc.code != 429:
                            raise
                else:
                    raise RateLimited(
                        f"facility {fid} {key}: still HTTP 429 after "
                        f"{sum(backoff)}s of backoff. The cache keeps everything "
                        f"already fetched — re-run later.") from exc
                if avail is None:
                    continue
            else:
                raise
        cache_entry.setdefault("months", {})[key] = month_string(avail, year, month)
        cache_entry["sites"] = max(cache_entry.get("sites", 0), len(avail))
        fetched += 1
        time.sleep(pause)
    if fetched:
        cache_entry["checked"] = datetime.date.today().isoformat()
    return fetched


def day_map(cache_entry):
    """{'MM-DD': 'o'|'c'} across every month ever observed, newest wins."""
    out = {}
    for key in sorted(cache_entry.get("months", {})):
        year, month = (int(x) for x in key.split("-"))
        for i, ch in enumerate(cache_entry["months"][key], start=1):
            if ch == UNKNOWN:
                continue
            out[f"{month:02d}-{i:02d}"] = ch
    return out


def _mmdd_ordinal(key):
    """Day-of-year position for an MM-DD key, on a leap year so 02-29 fits."""
    month, day = (int(x) for x in key.split("-"))
    return datetime.date(2024, month, day).timetuple().tm_yday


def smooth(days, min_run=MIN_RUN_DAYS):
    """Erase runs too short to be a season, so they cannot become edges.

    Erased rather than flipped to the neighbouring value: a three-day closure is
    not evidence the campground was OPEN either, and inventing the opposite
    reading would be the same mistake in the other direction. Unknown is the
    honest result, and it simply yields no edge there.
    """
    keys = sorted(days, key=_mmdd_ordinal)
    if not keys:
        return {}
    out = dict(days)
    runs, start = [], 0
    for i in range(1, len(keys) + 1):
        if i == len(keys) or days[keys[i]] != days[keys[start]]:
            runs.append((start, i - 1))
            start = i
    # A run spanning the new year is one run, not two.
    if (len(runs) > 1 and days[keys[0]] == days[keys[-1]]):
        first, last = runs[0], runs[-1]
        merged_len = (first[1] - first[0] + 1) + (last[1] - last[0] + 1)
        if merged_len >= min_run:
            runs = runs[1:-1]
    for lo, hi in runs:
        if hi - lo + 1 < min_run:
            for k in keys[lo:hi + 1]:
                out.pop(k, None)
    return out


def season_edges(days):
    """Observed open<->closed transitions as (kind, 'MM-DD') pairs.

    This is the whole derivation, and it is built on transitions rather than on
    coverage because a single run sees far less of the year than it first
    appears. Beyond each facility's own release window every date reads NYR, so
    a typical campground yields ~120 observed days out of 365 — the six-month
    booking horizon, not the calendar. Requiring most of a year before saying
    anything would mean saying nothing about almost every facility.

    An EDGE needs no such coverage. "Open on 10-15, closed on 10-16" is a fact
    about two days that were both observed, and it is exactly the fact worth
    recording. A facility can therefore contribute its closing date in autumn
    and its opening date only once a later run reaches the spring.
    """
    keys = sorted(days, key=_mmdd_ordinal)
    edges = []
    for i in range(len(keys)):
        here, nxt = keys[i], keys[(i + 1) % len(keys)]
        if days[here] == days[nxt]:
            continue
        gap = _mmdd_ordinal(nxt) - _mmdd_ordinal(here)
        if gap <= 0:
            gap += 366                     # wrapped through new year
        if gap > EDGE_MAX_GAP_DAYS:
            continue                       # too far apart to place the edge
        if days[here] == OPEN and days[nxt] == CLOSED:
            edges.append(("closes", here))
        elif days[here] == CLOSED and days[nxt] == OPEN:
            edges.append(("opens", nxt))
    return edges


def derive_season(cache_entry):
    """(season dict or None, reason). Never claims more than was observed."""
    raw = day_map(cache_entry)
    if not raw:
        return None, "no calendar data at all"
    days = smooth(raw)
    if not days:
        return None, f"{len(raw)} days observed, all in runs too short to read"
    closed = sum(1 for v in days.values() if v == CLOSED)

    edges = season_edges(days)
    opens = [d for kind, d in edges if kind == "opens"]
    closes = [d for kind, d in edges if kind == "closes"]

    # Year-round is a claim about days that were NOT observed, so it needs
    # near-complete coverage AND no transitions anywhere.
    if (len(days) >= MIN_DAYS_FOR_YEAR_ROUND and closed == 0 and not edges):
        return {"year_round": True}, f"{len(days)} days observed, none closed"

    season = {}
    if len(opens) == 1:
        season["opens"] = opens[0]
    if len(closes) == 1:
        season["closes"] = closes[0]
    if not season:
        if edges:
            return None, (f"{len(opens)} opening and {len(closes)} closing edges "
                          f"— ambiguous, needs a human")
        return None, (f"only {len(days)} days observed, no transition seen "
                      f"({closed} closed)")
    return season, (f"{len(days)} days observed, "
                    f"edges {'+'.join(k for k, _ in edges)}")


def fcfs_signal(cache_entry):
    """Share of observed days that were open. Advisory only, never written.

    A low share on a facility with no season edge is the interesting case: it
    suggests sites that are simply never bookable, which is what a walk-up
    campground looks like from the calendar. It is NOT proof — a maintenance
    closure, a group loop and a seasonal shutdown all read the same way — which
    is why this only ever prints.
    """
    days = day_map(cache_entry)
    if not days:
        return None
    return round(sum(1 for v in days.values() if v == OPEN) / len(days), 3)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write campgrounds.json")
    ap.add_argument("--limit", type=int, default=25,
                    help="how many facilities to WALK this run (cache makes "
                         "re-runs free); 0 = all")
    ap.add_argument("--only", type=int, nargs="*",
                    help="campground ids to walk, ignoring --limit")
    ap.add_argument("--months-back", type=int, default=3)
    ap.add_argument("--months-forward", type=int, default=8)
    ap.add_argument("--pause", type=float, default=1.0,
                    help="seconds between requests. The endpoint is undocumented "
                         "and rate-limits: 0.25s drew 429s within ~30 facilities, "
                         "1.0s did not. Raise it rather than retrying harder.")
    ap.add_argument("--max-age-days", type=int, default=0,
                    help="re-walk facilities whose cache is older than this")
    ap.add_argument("--fcfs", action="store_true",
                    help="report the first-come signal (never written)")
    ap.add_argument("--file", default=CAMPGROUNDS_JSON)
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        entries = json.load(f)
    by_id = {e["id"]: e for e in entries}
    facilities = facility_ids(entries)

    cache = {}
    if os.path.exists(CACHE_JSON):
        with open(CACHE_JSON, encoding="utf-8") as f:
            cache = json.load(f)

    today = datetime.date.today()
    months = []
    for offset in range(-args.months_back, args.months_forward + 1):
        m = today.month - 1 + offset
        months.append((today.year + m // 12, m % 12 + 1))

    if args.only:
        targets = [c for c in args.only if c in facilities]
    else:
        stale = []
        for cid, fid in facilities.items():
            got = cache.get(str(fid), {})
            if not got.get("months"):
                stale.append(cid)
            elif args.max_age_days:
                age = (today - datetime.date.fromisoformat(
                    got.get("checked", "1970-01-01"))).days
                if age >= args.max_age_days:
                    stale.append(cid)
        targets = stale if args.limit == 0 else stale[:args.limit]

    print(f"{len(facilities)} entries have a facility id; "
          f"{sum(1 for f in facilities.values() if cache.get(str(f), {}).get('months'))} "
          f"already cached; walking {len(targets)} this run")

    requests = 0
    stopped = None
    for n, cid in enumerate(targets, 1):
        fid = facilities[cid]
        # Build into a scratch entry and only commit it if something was
        # actually fetched, so a failed facility leaves NO cache record rather
        # than an empty one that reads as "this place has no calendar".
        entry = dict(cache.get(str(fid), {}))
        try:
            got = walk_months(fid, months, entry, pause=args.pause)
        except RateLimited as exc:
            stopped = str(exc)
            break
        except Exception as exc:                       # noqa: BLE001
            print(f"  [{cid}] {by_id[cid]['name'][:40]}: {type(exc).__name__} {exc}")
            continue
        if entry.get("months"):
            cache[str(fid)] = entry
            # Written after EVERY facility, not every few: this run may last
            # hours and be interrupted, and an unsaved batch is a batch of
            # requests spent against a rate limiter for nothing.
            os.makedirs(os.path.dirname(CACHE_JSON), exist_ok=True)
            with open(CACHE_JSON, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=1, sort_keys=True)
        requests += got
        if n % 10 == 0 or n == len(targets):
            print(f"  ...{n}/{len(targets)} facilities, {requests} requests",
                  flush=True)

    os.makedirs(os.path.dirname(CACHE_JSON), exist_ok=True)
    with open(CACHE_JSON, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=1, sort_keys=True)
    if stopped:
        print(f"\n  STOPPED EARLY: {stopped}")

    stats = Counter()
    changes = []
    for cid, fid in facilities.items():
        entry = cache.get(str(fid), {})
        if not entry.get("months"):
            stats["not walked yet"] += 1
            continue
        season, reason = derive_season(entry)
        if season is None:
            stats[f"no verdict: {reason.split('(')[0].strip()}"] += 1
            continue
        target = by_id[cid]
        existing = target.get("season")
        if existing == season:
            stats["already correct"] += 1
            continue
        scope = campground_schema.field_scope(target, "season", "opens") or "new"
        if existing and scope == "entry" and not (
                (target.get("provenance") or {}).get("season", {}).get("method")
                == "derived"):
            # A human-verified season outranks a calendar reading.
            stats["kept: verified by hand"] += 1
            continue
        stats["year-round" if season.get("year_round") else "seasonal"] += 1
        changes.append((cid, season, reason, existing))

    print()
    for key, count in stats.most_common():
        print(f"  {key:44} {count:5}")
    print(f"\n  would change: {len(changes)}")
    for cid, season, reason, existing in changes[:12]:
        was = f"  (was {existing})" if existing else ""
        print(f"    [{cid}] {by_id[cid]['name'][:40]:42} {season}  — {reason}{was}")

    if args.fcfs:
        print("\n── first-come signal (advisory, never written) ──")
        rows = []
        for cid, fid in facilities.items():
            sig = fcfs_signal(cache.get(str(fid), {}))
            if sig is not None:
                rows.append((sig, cid))
        rows.sort()
        print(f"    {len(rows)} facilities with data; "
              f"open-day share quartiles: "
              f"{[rows[int(len(rows)*q)][0] for q in (0.25, 0.5, 0.75)] if rows else '-'}")

    if not args.apply:
        print("\nDry run. Nothing written. Re-run with --apply to write.")
        return 0

    backup = f"{args.file}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(args.file, backup)
    for cid, season, reason, _ in changes:
        target = by_id[cid]
        campground_schema.apply_update(target, {
            "season": season,
            "provenance": {"season": {
                "source": f"recreation.gov availability calendar, facility "
                          f"{facilities[cid]} ({reason})",
                "checked": datetime.date.today().isoformat(),
                "method": "derived"}},
        })
    with open(args.file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nWrote {args.file} ({len(changes)} entries). Backup: {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
