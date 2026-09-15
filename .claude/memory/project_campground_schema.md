---
name: project-campground-schema
description: Structured campground fields (amenities/booking/fees/season) + agency policy registry — phases 1/2/4 + popup surfacing + map rating filter done; registry at 27 rows; phase 3 extraction is next
metadata:
  type: project
---

Structured-field project on `campgrounds.json`, started and largely built 2026-09-14.
Rules live in **`docs/campground-schema.md`** (read it first); this is only the status
and the things that are not written down there.

**Done:** schema vocabulary + deep-merge PUT + policy registry (`campground_schema.py`,
`campground_policies.json`); manage-form UI with tri-state selects; RV Life rating lifted
out of note prose into `rating` on 11,771 entries (`extract_rating.py`); rec.gov season
derivation (`recgov_calendar.py`); 27 registry rows covering 5,704 entries (44.7%) and 57.2%
of nights actually slept (`state:WV` added 2026-09-15).

**Map popup surfacing DONE 2026-09-14** (commit `95879c2`): verified and inherited chip
runs, the agency half attributed ("Typical for Indiana state parks") and withheld when
`_policy_label()` cannot name the agency; `resolve()` gained a per-group `inherited` key
list because group-level scope cannot split a `mixed` group; formatters shared with the
manage form in `static/campground-schema.js`. **The motivation is worth carrying forward:
phase 2 had emptied the RV Life rating out of note prose on 11,771 entries and the popup
renders the NOTE, so the pass made a published fact invisible.** Any extraction that moves
prose into a field owes the same debt — see doc §8.6.

**Map RATING FILTER DONE 2026-09-15** (commit `b52cd19`, doc §8.5 rewritten to describe it):
minimum stars + maximum `$` tier in the bottom-right box, now headed **Filters** with an
Ownership sub-heading. **Coverage is what picked the field, and measuring it first is the
transferable part** — `rating.stars`/`price_tier` sit on 76%/90% of entries while
`hookups`/`facilities`/`season` are at **0%** and every populated `booking`/`fees` value is
inherited from the registry (§3 forbids that being the sole reason to exclude). A filter on
a field nothing carries is a control that empties the map, so **measure coverage before
building the next one.** §2.2 is implemented as FADING (`fillOpacity` 0.25 — opacity is the
only free channel, the fill colour belongs to the legend) plus an "Include unrated" checkbox
on by default; the number that justifies it is that a naive `stars >= 4` shows 8,688 of
12,774 where the rule shows 11,694, so 3,006 (24%, mostly the public land RV Life never
rated) would have vanished silently. One box, not three: a third bottom-corner control costs
a phone ~90px even collapsed and the mobile `margin-bottom: 28px` rule applies to each, so
stacked boxes also open a dead gap. Payload measured before adding (§8.4): +20 KB gzipped,
~1%; a terse `s`/`p` encoding saved 3 KB more and wasn't worth unreadable client code.

**PHASE 3 SHIPPED 2026-09-15 as `extract_fields.py`** (doc §7 has the full write-up).
Reads `hookups`/`sites`/`facilities`/`season`/`booking` out of note prose via `claude-opus-5`;
the note itself is never edited. Things worth carrying forward that the doc does not stress:

- **The chunking design is the reusable part**, and AWH asked for it explicitly: "no huge
  unstoppable tasks that lose all their data if the session limit hits. Small chunks,
  sequentially, stoppable, easy to commit work." Batches of 12, N in flight, written in
  WAVES (one writer, so no lock), `--limit` per run, SIGINT finishes the wave. Progress
  lives in the DATA (`note_scan` = hash of the note that was read) rather than a cursor
  file, so resuming is just running it again. Exercised for real: a mid-run Ctrl-C finished
  its wave, wrote 144 entries and exited with a full summary. Use this shape for any future
  bulk pass over the library.
- **`note_scan` is written even when the note yields nothing.** That is the whole of the
  incrementality — without it the ~70% of notes with no structured fact are re-billed every
  pass. Same distinction as `detect_people.py`'s recorded 0. See [[feedback-absent-is-not-unknown]].
- **Effort was measured, not assumed** — `low` looked obviously right for "read a fact off a
  sentence" and was wrong: it MISSED four explicit facts out of 24 to save ~$2.60/1,000.
  Same for workers (1→53/min, 4→82, 16→338, no 429s).
- **Two prompt rules each cost a review round:** an approximate figure is still a figure
  ("rigs to ~45 ft" → 45) and `max_rig_ft` is dropped only when the note UNDERCUTS its own
  number; and a bare "reservable online" names no platform (an early version answered
  `operator`, inventing a channel).
- **Verify a sample against the notes by hand before a bulk run.** That is what caught the
  `operator` bug and confirmed every stored `false` traced to an explicit negative in the
  prose ("restrooms (no showers)", "no potable water", "no hookups").

**Not done:** Good Sam bulk match (phase 5); more registry rows (phase 6); manage-table sort
on the new fields; the NL corridor search that started the whole thread (deliberately
tabled).

**Next: more map filters, and RE-MEASURE COVERAGE FIRST.** The rating filter shipped the same
day on the argument that everything else was at 0%; phase 3 is falsifying that, so the choice
of the next filter has to be re-derived from `extract_fields.py --report` rather than from
anything written here. Doc §8.5 has the shape and §2.2 the rule that makes it non-trivial
(an unknown value is shown and flagged, never filtered out); §8.4 caps what may ride in the
inline marker payload. After that: phase 5, phase 6.

**Priority came from joining `trips.json` against `campgrounds.json` by nights slept**,
not entry count — that is what put PA/MD/VA ahead of MI/CA. Re-run that join before
picking the next rows — **`./policy_priority.py`** (committed 2026-09-15, read-only, no
args) is that join, and doc §5 names it. **Two traps it exists to hold:** `is_home_stay()`
reads `stay["place"]`, which only `parse_trips()` materializes (raw `trips.json` records
give a silent False and 23 home nights in the denominator), and family-kind entries carry
no `ownership`, so 47 driveway nights land in a bogus bucket unless excluded.

**The nights signal is now spent, as of the 2026-09-15 run.** Every row above the best
remaining agency is `private:*` / `hipcamp:*` / `local:*`, which doc §5 says to leave alone,
and the agency rows left are at 2 nights or fewer: `state:MA` (2 nights, 22 entries),
`state:GA` (1, 53), then nothing. So the next rows should be picked on **entries** or on a
trip actually being planned — `state:OR` (55), `state:GA` (53), `provincial:MB` (53),
`state:OK` (52), `provincial:SK` (52) lead that ranking; 961 entries across 34 rows remain.

**Realistic ceiling is ~52%.** `local:*` rows are mostly dead ends (`local:IA` is 245
entries across 245 different counties); Suffolk County worked only because it genuinely
is one authority.

**Watch items — schema gaps deliberately left open**, each seen once and awaiting a
second instance before extending the vocabulary: Hither Hills' one-reservation-per-
household peak-season limit; Virginia's non-resident surcharge scaling by site type
($5 standard → $8 full hookup); BC's maximum stay being per calendar year rather than
per visit.

**WV is the third row that could not state a booking window** (after IA's contradicted
cutoff and PA's absent non-resident rate), and the first with NO published rates at all —
West Virginia puts every number inside its Inntopia booking engine and nothing on the web.
The pre-online brochures still served from `wvstateparks.com` are the trap: they describe
held-back FCFS sites and a two-days-prior cutoff the current system contradicts, and a
search engine will hand you both as current.

**Unresolved:** Iowa's two official pages contradict each other on the booking cutoff,
and its post-cutoff FCFS is uncorroborated — resolve by phone. Florida's site 403s
automated fetch so its row is `method: reported`, not verified.

**Verifying map UI with no browser extension:** headless Firefox takes screenshots
(`firefox --headless --profile <scratch dir> --screenshot out.png --window-size=W,H <url>`)
— the separate profile is REQUIRED or it refuses while the user's own Firefox is running.
Log in for the shot by adding a temporary entry to `trip_data/share_tokens.json` and hitting
`/s/<token>?next=/campgrounds/map`: one GET authenticates and lands on the page, where a
password login cannot. Back up and restore both that file and `users.json`, and diff them
afterwards. A non-default control state (a filter already applied) is reachable by
temporarily editing the `STORE.get(..., default)` in the template, screenshotting, and
reverting.

See [[feedback-absent-is-not-unknown]], [[feedback-responsive-all-screens]],
[[reference-recgov-calendar-limits]] and [[reference-js-testing-without-node]] (how the
shared JS was verified with no browser — the rating filter's tests lift the predicates
verbatim out of the template and run them in quickjs against the real file).
