---
name: feedback-minimum-stay
description: "Minimum stays: since 2026-10-10 a standing 2-3 night minimum stays if clearly marked (booking.min_stay + dated note line); a 7-night summer minimum was dropped (Nickerson, AWH 2026-10-11); the old 2026-10-01 disqualify rule is kept as history"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 96da6df7-9a3e-4409-adaa-c37da68ef643
  modified: 2026-10-01T13:18:33.878Z
---

**SUPERSEDED 2026-10-10 (AWH): "from now on all campgrounds with a 2-night minimum can stay as long as it is clearly marked as such."** A standing minimum no longer disqualifies; instead mark it: `booking.min_stay` (+ `booking.note`, `provenance.booking` with source/date) and a dated "MINIMUM STAY: N nights ..." line appended to the note. Done for 1622, 14298, 13371, 4974 (3 nights), 3529 (3 nights summer). 3+ night standing minimums were kept the same way (4974); ask if a longer one turns up. docs/campground-curation.md states this rule since 2026-10-11 (AWH asked for the doc update). The history below explains the old rule.

OLD RULE: A campground whose minimum stay applies to EVERY stay is not a nightly campground and is skipped. **AWH 2026-10-01: a standing 2-night minimum disqualifies** ("a campground does not qualify if it has a standing 2-night minimum. Weekend is ok."). This tightened the 2026-09-30 rule, which drew the line at 4 nights (American Way RV Park, Mineral Wells WV: "$50 daily, 4 day minimum").

**Why:** EKKO trips move most days; a park that won't sell one night is a weekly/monthly park wearing a daily rate.

**How to apply:**
- Skip with kind_of_no "not nightly (N-night minimum)" when the minimum applies to all stays (Sparkman Lake OH, "two night minimum at all times", skipped 2026-10-01 though it passed at $40).
- Weekend 2-night and holiday 3-4-night minimums are normal and do NOT disqualify (River Ridge).
- A "2-night minimum except events" is a standing minimum, so it now FAILS (Groves, 14240, was passed under the old rule).
- A booking engine often shows the minimum when the operator's page doesn't; ask AWH about any hold settled from a ResNexus read.
- **Applies retroactively to ALL existing entries** (AWH 2026-10-01).
- **A minimum that can be got around for one night is NOT standing**: a late-booking waiver (OH/IN/VT "within N days"), a phone single night, walk-up/FCFS sites. SC state parks publish a year-round 2-night minimum, but AWH has booked single nights "multiple times at SC by calling the campground within a week of arrival" (trips 24/56/88), so all SC state parks stay; MA likewise (trip 16 booked two single nights at Harold Parker despite DCR's "2-day minimum"). The written agency policy is not the test; whether a single night is actually sold is. AWH confirmed 2026-10-01: "a minimum that applies online but can be waived by phone is fine" (Van Hook AR, Bay Ridge MI kept).

- **Canada no_rate follow-up examples (2026-10-08):** same-day single-night products are waivers, not standing minimums - Camping Union's "Nuitée Express" (bought after 16:00, out by 09:00), Lac-aux-Sables "one night accepted same day only", Camping du Parc "one night by phone 48 h ahead". Standing minimums found only by working the engine: Wigwam (every site on a July 2027 Tuesday said "minimum de 2 nuitées" on its reservationcamping.ca site page), Péninsule (engine nights list generated from 2), Coolbreeze ("2 nuits minimum en tout temps" on its rate page). Check per site/type, not the form's first select ([[reference-hidden-rates-playbook]]).

Related: [[feedback_exclude_seasonal_residential]].

**Re-opened 2026-10-11** ([[project-minimum-stay-reopen]]): the parks the old rule removed or skipped were re-read and 17 came back with their minimums marked. Three of those skips were misreads: an event-weekend minimum (Oscoda), a cabins-only line (Cardinal), and an engine that sells one night (Tiny House). Read what a minimum is attached to before calling it standing.

**Named exceptions (AWH 2026-10-10):** Grouseland Hospitality (671, PA; every site), Tosanak Recreation Area (13500, IA county; RV sites) and ALL NJ state campgrounds (Stokes 1818/1819 confirmed by AWH; the other 13 via regulation N.J.A.C. 7:2-6.7, which sets 2 nights for every non-group NJ state campsite) have standing 2-night minimums and are kept anyway; each has booking.min_stay and a dated note line. Don't remove them on this rule.

**Kept for now (AWH 2026-10-10, "keep for now", may be revisited):** Riverview RV Resort AL (4974, 3-night min), Hidden Valley OH (14298, 2 nights / 3 holidays), Georgia Mountain Fairgrounds GA (13371, 2-night per note), West Arbutus WI (3529, 3 nights on Memorial Day-Labor Day reservations). Don't remove them on this rule without asking.

**Dropped (AWH 2026-10-11): Nickerson Beach (1447, Nassau County NY), 7-night minimum Memorial Day - Labor Day** on its 2026 rate card. It had been priced and marked under the 2026-10-10 rule and was raised only because it was longer than any minimum kept so far; AWH said drop and gave no reason.

**4+ nights, AWH 2026-10-12: drop every time so far.** Alcona Park MI (3996, 5 nights June 25 - Aug 15 on reservations) and The Landing on Red Gut Bay ON (8367, '4 Day minimum charge') were dropped, and American Way RV Park WV (4 nights) was left out. 2- and 3-night minimums stay and get marked (Jack Guthrie TX, 3 nights on reservations, marked 2026-10-12). How to apply: raise a 4+ night minimum as a likely drop, citing these. Red Gut Bay's line heads its rates page above the cabin table, so it may have been the cabins' only; read what a minimum is attached to before raising it.

**Sweep notes misstate minimums often (2026-10-12 follow-up, 43 checked):** a booking lead time was written as a minimum twice (Clackamas County's 'reservations must be made a minimum of 3 days ... in advance' became Metzler's '3-night min'; a rec.gov 4-day reservation cutoff became Twin Lakes WI's '4-day min'), and weekend or holiday rules were written unscoped (Maine state parks, Chippewa MN, Driftwood IL). Before marking or dropping on a note's minimum, read the operator's sentence or try one weeknight in the booking engine.
