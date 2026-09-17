---
name: project-campground-schema
description: Structured campground fields (amenities/booking/fees/season) + agency policy registry — phases 1/2/4 + popup surfacing + map rating filter done; registry at 27 rows; phase 3 extraction is next
metadata: 
  node_type: memory
  type: project
  originSessionId: a9cf38ab-6047-479a-a981-ab7343bcae7a
  modified: 2026-09-16T17:09:58.945Z
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

**PHASE 3 IS PAUSED PART-WAY: 10,186 of 12,689 notes scanned (80%), 2,503 left**
(as of commit `fce7d7c`, notes through id 10579). Coverage: hookups 62.9%,
booking 62.5%, sites 61.4%, facilities 49.2%, season 23.4%.
**Remaining states, in order:** CA 854, OR 592, AZ 279, QC 160, NV 121, ON 84,
NS 81, NB 76 (plus smaller pockets). **Washington is now fully done** — this
run (six batches, notes 10217-10579) covered the rest of Mt Baker-Snoqualmie/
Okanogan-Wenatchee/Olympic/Gifford Pinchot NF drainages, Colville NF (Kettle
River/Sullivan Lake/Pend Oreille), Lake Roosevelt NRA, North Cascades NP,
the full WA State Parks roster (Pacific coast, Puget Sound, San Juans,
Columbia River/Gorge, Cascades), then a long tail of county fairgrounds,
port-district, PUD/utility, tribal and private RV parks across the state.
Oregon is next per `--report`. **Resume with `./extract_fields.py --dump 60`
immediately — no state was left mid-batch.**

**Recurring judgment calls settled during the WA run, worth reusing:**
- **A named hookup SUBSET implies the unnamed utility is absent.** "partial-hookup
  (water/electric)" or "utility (elec/water)" → `water: true`, `sewer: false` (electric
  amp omitted unless a number is given) — the type name IS the inventory, so what it
  doesn't list isn't there. Reserve `sewer: true` for "full hookup" / an explicit sewer
  mention. This reading was applied consistently across ~40 entries; revisit if a
  counterexample turns up (a "partial-hookup" site that turns out to have sewer too).
- **"Non-hookup" / "no-hookup" sites are a fourth trigger phrase** alongside "no hookups"/
  "primitive"/"non-electric" in the doc's list — treated as equivalent (electric 0, water
  false, sewer false).
- **"Pit toilets" and a bare "toilet"/"restroom" (type unnamed) map differently**: pit
  toilet → `vault_toilets: true` (same fixture, different name); a bare "toilet"/
  "restroom" with no type word → omit per the doc's existing flush-vs-vault rule.
- **Two reservation channels named in one note (e.g. "by phone or via RoverPass/Hipcamp")**
  → pick the named third-party platform over `phone` (phone is the fallback when nothing
  else is named, not equal-priority with a real platform word).
- **A stated total that doesn't quite match the sum of subcategories** ("40 campsites: 8
  full-hookup, 24 standard, 5 equestrian, 1 hiker/biker" summing to 38) → trust the
  directly-stated total over re-deriving it, since the note author had the real count and
  the category breakdown may have a typo or omitted category.
- **"Open year-round except an annual N-day closure"** (e.g. "except Dec 20-Jan 1") →
  still `year_round: true`, deferring to the note's own words over the literal exception;
  a temporary/one-off closure (construction, fire damage, flood) never sets `year_round`
  either way regardless of duration.

**More conventions settled over the Saskatchewan/Manitoba/Idaho tail of that
run, beyond what the Alberta section below already covers:**
- **Same "province-wide agency portal earns no platform" rule extends to
  SKPP/Sask Parks and Manitoba's goingtocamp**, exactly like Alberta Parks
  and Parks Canada below. `recreation.gov` and `reserveamerica` still get
  named when the note spells one out (or names "ReserveAmerica SKPP" — SKPP's
  own reservation system runs on ReserveAmerica, confirmed by sibling notes
  that spell it out in full next to others that just say "Sask Parks").
- **A note naming TWO concrete channels with no clear primary** ("online/by
  phone", "phone/email or website", "Campspot or by phone", "in person,
  phone, or online") -> `reservable: true` with platform omitted every time,
  even when one of the two is a named enum value — picking one would be a
  guess. Exception: "phone/email" alone (no third "online") still resolves to
  `platform: "phone"`, matching the pre-existing data precedent this was
  checked against.
- **"100% reservable" / "fully reservable" / "reservation only" / "no
  self-registration" / "no FCFS"** -> `fcfs: "never"`, not just `reservable:
  true` — matches the existing "reservations required" -> never convention.
- **A range for any numeric field ("12-18 sites", "25-32 ft", "50-63 sites")
  is always omitted, never split-the-difference** — consistent with the
  existing "skip ranges" rule for counts, extended here to `max_rig_ft`
  ranges too, which came up constantly in Idaho USFS notes citing
  reviewer-reported rig-length ranges.
- **A temporary outage/closure note (wildfire, hazard-tree removal, "no water
  summer 2026", repairs) is never encoded as a permanent `false`** — omit the
  affected keys rather than assert a durable fact about a fixable, dated
  condition. Came up constantly in the Idaho/Alberta forest-service entries.
- **"Book direct" == "reservable via/by the operator"** — both phrasings
  point at the campground's own booking system as opposed to a third-party
  platform, and both map to `platform: "operator"`.

**A long run of Alberta Parks provincial/PRA campgrounds (8826-9005) settled a
few more conventions, all confirmed against already-scanned precedent:**
- **"Walk-in tent sites" are excluded from `sites.count`** unless the note
  itself states a combined total (e.g. "10 sites: 7 walk-in + 3 vehicle" ->
  10; "16 unserviced ... plus 3 walk-in" with no combined figure -> 16). Same
  exclusion as group/equestrian sites. The existing corpus is actually split
  on this (checked both ways), but exclusion is the more common prior pattern
  and the more conservative reading of "total campsites."
- **A subset that stays open/FCFS through the off-season does NOT flip
  `season.year_round` to true** when it's a small minority of the campground
  (a few sites of hundreds) — matches the existing "Loop A FCFS year-round"
  precedent. It only goes to `true` when the note frames the MAJORITY as
  continuous (e.g. "47 of 61 sites powered year-round").
- **`fcfs: "some_sites"`** for an explicit "mix of reservable and FCFS"
  statement, as opposed to `after_cutoff` for a genuine within-season DATE
  switch ("reservable May-Sep, sites 186-195 add FCFS after early Sep").
- **A facility named as being at a DIFFERENT loop/location within the same
  park ("showers available at nearby Lakeview loop", "dump station in nearby
  Lac La Biche") is treated as off-site — omitted or `false`, never claimed
  for the entry being scanned** — same rule as the existing "dump station 6
  blocks away" convention, just extended to showers/potable water and to
  "nearby"/loop-level phrasing, not only literal distances.
- **"Reservable via/by the operator"** (an explicit, singular, named booking
  party — a concessionaire like West Fraser Mills, not a province-wide
  agency) -> `platform: "operator"`. But "Reservable via Alberta Parks" (the
  province-wide portal covering hundreds of parks) still gets **no platform**,
  same as the Parks Canada precedent — the agency itself isn't in the enum
  and isn't a single campground's own system.
- **A temporary 2026 outage note** ("showers/flush toilets closed for repairs,
  alt sani-dump elsewhere") was NOT encoded as a permanent `false` — omitted
  those keys rather than asserting a durable fact about a fixable outage.

**New wrinkle handled in the Parks Canada / Banff / Jasper / Kananaskis batch
(8766-8825):** several notes give `max_rig_ft` only in metres ("RVs/trailers to
10 m"). Converted to feet by arithmetic (10 m -> 33 ft) since the audit script's
own docstring already treats unit conversion as an expected source of "number
not in note" flags (same bucket as "3-week max stay" -> 21 nights). Where a
note already carried a parenthetical (e.g. "8.2m (27')") that number was used
directly rather than recomputed. Also settled: "reservable via/through Parks
Canada" -> `reservable: true` with **no** platform (Parks Canada isn't in the
platform enum and isn't a third-party channel to point at) — matches
already-scanned entries 8265/8573. A season that is reservable in the main
window and FCFS in the shoulder (or a summer/winter-loop split covering the
whole year) -> `fcfs: "after_cutoff"`, matching the existing USACE/USFS
"reservable in peak season, FCFS off-peak" convention already in the data.
The API account ran out of credit at 7,544 (AWH 2026-09-15: "we won't be getting more API
credits for the time being"), so the last 482 were done by reading the notes in-session and
feeding them back through `--apply-file`. **To resume, with or without credits:**

    ./extract_fields.py --report                        # free, what is left
    ./extract_fields.py --limit 4700 --workers 16       # with API credit
    ./extract_fields.py --dump 60                       # without: read them yourself,
    ./extract_fields.py --apply-file proposals.json     #   same validation + write path

Nothing is half-done and there is no cursor to repair — `--dump` always returns what is
still queued. Coverage at the pause: hookups 48%, booking 45%, sites 45%, facilities 35%,
season 17%. Everything is committed and deployed to PA through commit `d62464d`; the ten
hand-extracted batches after that are committed locally but **not yet pushed**.

**Quality was checked, not assumed.** `./audit_extracted_fields.py` re-reads every derived
value against its own note; it flags ~5% and the flags are overwhelmingly benign (the doc and
the script's own docstring list which). It found exactly one real error in the first 3,675
numbers — a "15-amp electric only" rounded up to the enum's 20 — now fixed, with the rule
"never round up to reach an allowed value" in the prompt. The hand pass shows the same flag
profile as the API pass, so the two are interchangeable in quality.

**One judgement call applied uniformly** and worth revisiting if it looks wrong: where a note
says "individual sites first-come, first-served; group sites reservable", the entry gets
`reservable: false` / `fcfs: always`, because an RVer looking for a site cannot reserve one.

### Resuming the hand pass on another machine (written 2026-09-15 for the next session)

Assume **no API credit**. The loop is two commands per batch, and it is stateless — just
start it:

    ./extract_fields.py --dump 60          # read the 60 notes it prints
    ./extract_fields.py --apply-file <path to your JSON>   # then: git add -u && git commit

**Read `SYSTEM` in `extract_fields.py` before the first batch and follow it literally.** It
is the same prompt the API pass used and nearly every rule in it is a mistake that was made
and caught. The ones that come up constantly:

- **Absent is unknown.** Emit a key only when the note says it. Most entries yield two or
  three keys, and `{}` is a fine answer. Never write `false` for "not mentioned".
- `electric` is one of 0/20/30/50 and **nothing else** — "electric sites" with no amperage
  OMITS the key; "50/30-amp" is 50; "50 & 60-amp" is 50 (highest ALLOWED value genuinely
  offered); "15-amp only" omits it (never round up to reach an allowed value).
- "full hookup" = water+sewer true, electric only if the amperage is stated.
- "no hookups" = electric 0, water false, sewer false. "primitive"/"non-electric" = electric 0.
- A **dump station is not a sewer hookup**, and "dump station ~6 blocks away" / "sani-dump nearby" is `dump: false` (the note says it is elsewhere). Committed data is inconsistent here (18 false vs 25 omitted as of 2026-09-16).
- `max_rig_ft`: an approximate figure is still a figure ("rigs to ~45 ft" -> 45). Omit only
  when the note UNDERCUTS its own number ("max ~40 ft, tight spacing, best for smaller rigs")
  or gives a bare range ("24-32 ft"). A pad dimension ("40x15") is not a rig limit.
- `platform` only when the channel is NAMED. A bare "reservable online" names none.
- `season.opens/closes` for day-level dates, **tilde included** (AWH 2026-09-16: "~Apr 15-Oct 15" shifts a little each year, often to a weekend, but it still says the place is shut in December). Omit alternatives ("Apr 15/May 1") and month-only; a stated season with no dates still gives `year_round: false`. Only 6 of the first 250 scanned tilde-date notes got dates under the old rule.
- **Sonnet is fit for this** (2026-09-16 blind re-run of 8585-8644: 398/427 values agreed, a similar number of clear errors on each side). Spot-check a batch against the committed data now and then.
- Counts: use a stated total or an unambiguous sum; skip ranges ("128-130", "~18-22").

**Practicalities:** batches of 60 cost roughly 20K tokens round-trip and one commit each;
write the JSON with a heredoc to a scratch file, not into the repo. Run
`./audit_extracted_fields.py` every several batches — a ~5% flag rate in the known-benign
categories is normal and healthy; a NEW category appearing is the signal to stop and look.
`python -m unittest tests.test_extract_fields` needs no API and no network.

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
