---
name: reference-recgov-calendar-limits
description: What the keyless recreation.gov availability calendar can and cannot answer — statuses, rolling window, rate limits, and why FCFS is not derivable
metadata:
  type: reference
---

The recreation.gov availability endpoint (`AVAIL_URL` in `ridb/fetch_facility.py`) is a
keyless sibling of RIDB. Measured 2026-09-14 while building `recgov_calendar.py`:

- **Statuses:** `Available` / `Reserved` / `Open` = in service. `Not Reservable` = closed
  that night. **`NYR` = "not yet released" and carries NO information** — treating it as
  closed reports the entire federal system shutting exactly six months out.
- **Window is rolling, ~3 months back to ~8 forward.** Outside it, HTTP 400 — the window's
  edge, not an error.
- **One run sees ~120 days of the year, not 365**, because past each facility's own release
  window everything is NYR. Season data therefore has to ACCUMULATE across runs months apart.
- **FCFS is not derivable.** A walk-up campground has nothing to reserve, so it returns no
  campsites or `Not Reservable` everywhere — byte-identical to one shut for the winter.
- **Rate limits hard.** 0.25s between requests drew 429s within 30 facilities; 1.2s still
  did, because a burst is held against you long afterwards. Back off in minutes, not seconds.
- **Measured on South Dakota, 2026-09-20: a first walk of a region yields essentially
  nothing.** 23 of the 27 SD federal facilities were walked (the run was killed in a 429
  backoff, which cost nothing — the cache keeps every month already fetched). Exactly ONE
  produced a verdict, Elk Mountain at Wind Cave, year-round, which was already recorded. The
  Black Hills NF campgrounds each returned ~100 open days with no transition, and a cluster
  of them (Rod & Gun, Timon, Hanna, Dalton Lake, Ditch Creek, Beaver Creek, Castle Peak,
  Boxelder Forks) returned 21 days, all closed — too little to tell a winter closure from a
  facility that simply is not taking bookings. **So don't walk a region expecting an answer
  this season**; walk it to start the accrual.
- **The accrual is TRACKED: `audit/recgov_calendar.json`** (moved out of `trip_data/` and
  committed 2026-09-21; it had been gitignored only incidentally and was in no backup).
  **It is not a cache — it is the only copy.** Once the window rolls past a month, nobody
  can fetch that month again, so a lost file is lost observations, not a re-run. Commit it
  after every walk, and note it is the one thing here that gets MORE valuable with age.
- **Measured at scale 2026-09-21: the full walk yields ~14%.** 2,290 of 2,308 linked
  facilities, twelve months each, applied 323 seasons (208 seasonal, 115 year-round) and
  left **1,943 with no verdict** — 115 with no calendar data at all, the rest holding too
  few observed days to show a transition. Season coverage went 30.6% -> 32.7%. So a
  region-wide walk is worth applying, but the bulk still waits on accrual.
- **The Labor-Day check is how you tell a real closure from a window artifact.** 146 of 186
  `closes` edges landed in September, which looks exactly like the booking window being
  misread — but the most common single date was **09-07 with 37 campgrounds (Labor Day
  2026)** and the next four were Saturdays and a Sunday. Real closures fall on holidays and
  weekends; a window artifact would not. Run that check before trusting a September-heavy
  batch.
- **The days around the fetch date read Not Reservable whatever the season** (measured 2026-10-12 at
  Lane Spring: the ten days back and four ahead, every site, then Available). The 2026-09-21 walk
  turned that band into 'opens 09-24'-style seasons at ten campgrounds open all summer; AWH had them
  cleared (commit 21d120e). `recgov_calendar.py` now drops the edges bordering a closed run lying
  wholly within 14 days of its month's fetch date (`fetched` per month) when an open day follows.
  It drops only the EDGES: erasing the run instead merged the open days around it into ~75 new
  unchecked closing dates. The early-September closes (09-07..09-13) are untouched, but their
  exact day is only good to about two weeks: the band starts ~11 days before the fetch, so the last
  'Reserved' night before it (a weekend, Labor Day) becomes the edge. That also weakens the
  Labor-Day check below as proof of a real closure.
- **Second full walk, 2026-10-20: 2,429 facilities, 30 applied (24 year-round).** The first dry run
  proposed 120. Three fixes, all now in `recgov_calendar.py` with tests:
  - **Past ~6 months, some facilities answer Not Reservable instead of NYR.** June 2027, fetched
    225 days out, read closed throughout for 28 campgrounds, giving "opens 07-01" at the month
    boundary. A closed reading over 183 days out now counts only if the same fetch showed an
    open day at least as far ahead (Blue Bend's real 05-01 opening passes that test).
  - **A day two years read differently is left unknown.** The newer reading no longer wins.
  - **A year-round verdict REPLACES the season group.** It used to deep-merge, which left
    `year_round: true` beside the old dates, and **a calendar closure never overturns
    year-round.** Koomer Ridge, Putah Canyon and Rio Grande (Creede) are reservable in summer
    and first-come the rest of the year, which is the FCFS trap above. Mather's
    "03-01 to 11-30" was its reservation window.
- **Some facility ids 404.** Ten of the entries' `/camping/campgrounds/<id>` links returned
  HTTP 404 — the calendar is gone, not empty. They stay unwalked and are worth a look as a
  data-quality signal (renamed or retired facility).
- ~2,283 entries carry a `/camping/campgrounds/<id>` link; `/camping/poi/<id>` ones are
  dispersed areas with no calendar. Full walk is ~27,000 requests — a multi-day job.
