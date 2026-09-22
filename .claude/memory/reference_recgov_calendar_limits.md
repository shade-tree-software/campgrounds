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
- **Some facility ids 404.** Ten of the entries' `/camping/campgrounds/<id>` links returned
  HTTP 404 — the calendar is gone, not empty. They stay unwalked and are worth a look as a
  data-quality signal (renamed or retired facility).
- ~2,283 entries carry a `/camping/campgrounds/<id>` link; `/camping/poi/<id>` ones are
  dispersed areas with no calendar. Full walk is ~27,000 requests — a multi-day job.
