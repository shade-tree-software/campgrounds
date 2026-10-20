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
observations ACCUMULATE in `audit/recgov_calendar.json` and the season is
re-derived from everything ever seen. A run in spring fills the opening edge a
run in autumn could not reach.

**That cache is TRACKED IN GIT, and it is not regenerable.** Once the rolling
window moves past a month, that month's observations cannot be fetched again by
anyone — so the file is the only copy of what was seen, not a cache of what
could be seen again. It lived untracked under `trip_data/` until 2026-09-21,
protected by neither git nor `backup.sh`; commit it after every walk.

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
CACHE_JSON = os.path.join("audit", "recgov_calendar.json")

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
# rec.gov reports the days just behind the date a month is fetched, and the few
# days ahead before a campground stops taking bookings, as Not Reservable on
# every site whatever the season. Measured 2026-10-12 at Lane Spring (MO): the
# ten days back and the four ahead all read Not Reservable, then Available. The
# 2026-09-21 walk read that band as a closure and wrote "opens 09-24" and the
# like for ten campgrounds open all summer (Whitehorse, Camp 9, Greenville ...).
# So a closed run lying wholly within this many days of its fetch date and
# followed by an open day yields no edge on either side. Only the edges go: the
# run itself stays, because erasing it lets the open days around it merge into
# new edges nobody checked (75 of them on that walk). A closed run reaching past
# the window either way is still read; the result was the same at 7 days as 14.
FETCH_WINDOW_DAYS = 14
# rec.gov releases campsites up to six months ahead, and past that some
# facilities answer Not Reservable on every date rather than NYR. The 2026-10-20
# walk read June 2027 (fetched 225 days out) as closed for 28 campgrounds whose
# June 2026 had shown open days, and wrote "opens 07-01" at the month boundary.
# A closed reading further out than this is no information UNLESS the same
# fetch showed an open day at least as far ahead, which proves its window
# reached there: Blue Bend, fetched 2026-09-20, read April 2027 closed and May
# open, a real opening. An open reading always counts.
BOOKING_HORIZON_DAYS = 183


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


# Slack past a facility's predicted booking horizon (see window_reach): some
# windows open a whole month at a time rather than rolling day by day.
WINDOW_REACH_SLACK_DAYS = 31


def window_reach(cache_entry, today=None):
    """The furthest date this facility's booking window can have reached by now,
    or None if no day of it was ever observed.

    The last day a month showed anything but NYR was the window's edge on the
    day that month was fetched; a rolling window has moved on by as long since.
    """
    today = today or datetime.date.today()
    fetched = cache_entry.get("fetched") or {}
    best = None
    for key, days in cache_entry.get("months", {}).items():
        seen = [i for i, c in enumerate(days) if c != UNKNOWN]
        on = fetched.get(key) or cache_entry.get("checked")
        if not seen or not on:
            continue
        edge = datetime.date(int(key[:4]), int(key[5:7]), seen[-1] + 1)
        edge += today - datetime.date.fromisoformat(on)
        best = edge if best is None or edge > best else best
    if best is None:
        return None
    return best + datetime.timedelta(days=WINDOW_REACH_SLACK_DAYS)


def walk_months(fid, months, cache_entry, pause=1.0, backoff=(60, 180, 420)):
    """Fetch each (year, month) not already cached, or cached as all-NYR and
    not yet past. Returns how many were hit.

    Each month's fetch date goes in `fetched` (see FETCH_WINDOW_DAYS). Entries
    cached before 2026-10-12 carry only `checked`, which was then the date all
    their months were fetched, so it is pinned onto them before it moves on.
    """
    fetched = 0
    if cache_entry.get("months") and "fetched" not in cache_entry:
        cache_entry["fetched"] = {key: cache_entry.get("checked")
                                  for key in cache_entry["months"]}
    this_month = datetime.date.today().strftime("%Y-%m")
    reach = window_reach(cache_entry)
    for year, month in months:
        key = f"{year:04d}-{month:02d}"
        held = cache_entry.get("months", {}).get(key)
        # A month that read entirely NYR held no information, only the booking
        # window's edge on the day it was fetched, so it is asked again once the
        # window may have reached it. Skipping every cached month (until
        # 2026-10-20) froze the 2026-09 walk's ~13k all-NYR months in place
        # forever: the spring a later run was meant to fill in could never
        # arrive. A month with ANY observation stays as it is, and a past month
        # is not asked again (it can only have left the window).
        if held is not None and (set(held) != {UNKNOWN} or key < this_month
                                 or reach is None):
            continue
        # Nor is a month the window cannot have reached yet: it would only read
        # NYR again. That halves a re-walk (13,167 all-NYR months -> 6,863 on
        # 2026-10-20). A facility never observed at all has no reach and is
        # walked as before.
        if reach is not None and datetime.date(year, month, 1) > reach:
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
        cache_entry.setdefault("fetched", {})[key] = datetime.date.today().isoformat()
        cache_entry["sites"] = max(cache_entry.get("sites", 0), len(avail))
        fetched += 1
        time.sleep(pause)
    if fetched:
        cache_entry["checked"] = datetime.date.today().isoformat()
    return fetched


def _readings(cache_entry):
    """(MM-DD, char, days from its month's fetch date or None) for every
    observed day, months in key order."""
    fetched = cache_entry.get("fetched") or {}
    for key in sorted(cache_entry.get("months", {})):
        year, month = (int(x) for x in key.split("-"))
        when = fetched.get(key) or cache_entry.get("checked")
        when = datetime.date.fromisoformat(when) if when else None
        for i, ch in enumerate(cache_entry["months"][key], start=1):
            if ch == UNKNOWN:
                continue
            offset = (datetime.date(year, month, i) - when).days if when else None
            yield f"{month:02d}-{i:02d}", ch, offset, when


def day_map(cache_entry):
    """{'MM-DD': 'o'|'c'} across every month ever observed.

    A day two years read differently is dropped, not settled by the newer one,
    and a closed reading past the booking horizon counts only where the same
    fetch showed an open day at least as far out (see BOOKING_HORIZON_DAYS).
    Letting the newer reading win, with no horizon, had June 2027 overwrite the
    open days June 2026 had shown (Clear Lake 2355, open from 06-22). Unknown is
    the honest reading of a disagreement, and it yields no edge.
    """
    readings = list(_readings(cache_entry))
    reach = {}
    for _, ch, offset, when in readings:
        if ch == OPEN and offset is not None:
            reach[when] = max(reach.get(when, offset), offset)
    out, conflict = {}, set()
    for mmdd, ch, offset, when in readings:
        if (ch == CLOSED and offset is not None and offset > BOOKING_HORIZON_DAYS
                and offset > reach.get(when, offset - 1)):
            continue
        if out.get(mmdd, ch) != ch:
            conflict.add(mmdd)
        out[mmdd] = ch
    for mmdd in conflict:
        del out[mmdd]
    return out


def _fetch_offsets(cache_entry):
    """{'MM-DD': days from its month's fetch date to that day}, for the reading
    day_map keeps (newest wins, as there); None where no fetch date is known."""
    fetched = cache_entry.get("fetched") or {}
    out = {}
    for key in sorted(cache_entry.get("months", {})):
        year, month = (int(x) for x in key.split("-"))
        when = fetched.get(key) or cache_entry.get("checked")
        when = datetime.date.fromisoformat(when) if when else None
        for i, ch in enumerate(cache_entry["months"][key], start=1):
            if ch == UNKNOWN:
                continue
            out[f"{month:02d}-{i:02d}"] = (
                (datetime.date(year, month, i) - when).days if when else None)
    return out


def _mmdd_ordinal(key):
    """Day-of-year position for an MM-DD key, on a leap year so 02-29 fits."""
    month, day = (int(x) for x in key.split("-"))
    return datetime.date(2024, month, day).timetuple().tm_yday


def _runs(days):
    """Runs of one value over the observed days in calendar order, as lists of
    MM-DD keys. A run spanning the new year is one run, not two."""
    runs = []
    for key in sorted(days, key=_mmdd_ordinal):
        if runs and days[runs[-1][-1]] == days[key]:
            runs[-1].append(key)
        else:
            runs.append([key])
    if len(runs) > 1 and days[runs[0][0]] == days[runs[-1][-1]]:
        runs[0] = runs.pop() + runs[0]
    return runs


def fetch_window_edges(cache_entry, days):
    """Edges bordering a closed run of `days` that is only the booking window
    around its fetch date (see FETCH_WINDOW_DAYS): every day of the run within
    that many days of its fetch date, and an open day right after it."""
    offsets = _fetch_offsets(cache_entry)
    runs = _runs(days)
    out = set()
    for i, run in enumerate(runs):
        if len(runs) < 2 or days[run[0]] != CLOSED:
            continue
        if not all(offsets[k] is not None and abs(offsets[k]) <= FETCH_WINDOW_DAYS
                   for k in run):
            continue
        before, after = runs[i - 1], runs[(i + 1) % len(runs)]
        gap = _mmdd_ordinal(after[0]) - _mmdd_ordinal(run[-1])
        if gap <= 0:
            gap += 366
        if gap <= EDGE_MAX_GAP_DAYS:
            out |= {("closes", before[-1]), ("opens", after[0])}
    return out


def smooth(days, min_run=MIN_RUN_DAYS):
    """Erase runs too short to be a season, so they cannot become edges.

    Erased rather than flipped to the neighbouring value: a three-day closure is
    not evidence the campground was OPEN either, and inventing the opposite
    reading would be the same mistake in the other direction. Unknown is the
    honest result, and it simply yields no edge there.
    """
    out = dict(days)
    for run in _runs(days):
        if len(run) < min_run:
            for k in run:
                del out[k]
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

    # Year-round is a claim about days that were NOT observed, so it needs
    # near-complete coverage AND no transitions anywhere.
    if (len(days) >= MIN_DAYS_FOR_YEAR_ROUND and closed == 0 and not edges):
        return {"year_round": True}, f"{len(days)} days observed, none closed"

    observed = edges
    edges = [e for e in observed if e not in fetch_window_edges(cache_entry, days)]
    opens = [d for kind, d in edges if kind == "opens"]
    closes = [d for kind, d in edges if kind == "closes"]

    season = {}
    if len(opens) == 1:
        season["opens"] = opens[0]
    if len(closes) == 1:
        season["closes"] = closes[0]
    if not season:
        if edges:
            return None, (f"{len(opens)} opening and {len(closes)} closing edges "
                          f"— ambiguous, needs a human")
        if observed:
            return None, (f"{len(days)} days observed, the only transition is "
                          f"the booking window around the fetch date")
        return None, (f"only {len(days)} days observed, no transition seen "
                      f"({closed} closed)")
    return season, (f"{len(days)} days observed, "
                    f"edges {'+'.join(k for k, _ in edges)}")


def resulting_season(existing, season):
    """The season group as it should read after a calendar verdict.

    A year-round verdict replaces the group: bookable days all year outrank the
    dates a note gave (Mather's 03-01 to 11-30 was its reservation window), and
    merging left "year_round: true" beside an opening date. A seasonal verdict
    merges, so an edge an earlier walk saw and this one could not reach stays.
    """
    if season.get("year_round"):
        return dict(season)
    merged = dict(existing or {})
    merged.update(season)
    return merged


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
    ap.add_argument("--show", type=int, default=12,
                    help="how many proposed changes to list")
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
        if (existing or {}).get("year_round") is True and not season.get("year_round"):
            # Not Reservable is also what a first-come off-season looks like
            # (Koomer Ridge, Putah Canyon: reservable in summer, open all year),
            # so a calendar closure never overturns a year-round season.
            stats["kept: year-round (closed may be first-come)"] += 1
            continue
        season = resulting_season(existing, season)
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
    for cid, season, reason, existing in changes[:args.show]:
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
        target["season"] = season
        campground_schema.apply_update(target, {
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
