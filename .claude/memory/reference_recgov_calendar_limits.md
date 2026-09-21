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
  this season**; walk it to start the accrual. Note the cache is gitignored, so the accrual
  lives on whichever machine ran it.
- ~2,283 entries carry a `/camping/campgrounds/<id>` link; `/camping/poi/<id>` ones are
  dispersed areas with no calendar. Full walk is ~27,000 requests — a multi-day job.
