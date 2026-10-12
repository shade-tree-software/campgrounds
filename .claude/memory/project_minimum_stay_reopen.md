---
name: project-minimum-stay-reopen
description: "2026-10-11/12 re-open of everything the old standing-minimum rule removed or skipped (17 back, ids 15342-15358; Lac Libby 15359 and Red Gut Bay 15360 after AWH's answers; Goethe, Péninsule, Alcona, South Bay dropped), plus the 2026-10-12 follow-up that marked or corrected 43 existing entries; next id 15361"
metadata:
  node_type: memory
  type: project
  originSessionId: 697b5c76-5652-4131-bd7c-1761a58eb19c
  modified: 2026-10-12T01:33:38.858Z
---

**Done 2026-10-11, commits 15148f0 (restores), a8f533c (US skips) and the Canada batch after them.** AWH said yes to re-opening the parks that the old rule (2026-10-01 to 2026-10-10, a standing 2-night minimum disqualifies) removed or skipped, after [[feedback-minimum-stay]] changed to keep-and-mark. Record: `audit/minimum_stay_reopen/decisions.json` (one verdict per candidate: restore / add / mark / skip / ask), `apply.py` writes them, `removed_records.json` holds the removed entries taken from git. Progress lives in the data: written entries carry `re-opened 2026-10-11` in inclusion_evidence.

**Result:**
- Restored under new ids: Riverside Landing MO 15342, Evening Star MO 15343, Oscoda County MI 15344, Barnes Park MI 15345, Groves of Michigan 15346, Eagles Landing SD 15347.
- Already back in the database, so their minimums were marked in place: Millbrook VT 14369 and Goethe Trailhead FL 14396. A sweep had re-added both the same day their old entries were removed.
- US adds: Sparkman Lake OH 15348, Little Switzerland MI 15349, Bear Lake (Manawa) WI 15350, Cardinal NY 15351, Tiny House Adventures MO 15352, Beech Lake TN 15353.
- Canada adds: Wigwam QC 15354, Parc de la Péninsule QC 15355, Lac Morin QC 15356, Netley Creek MB 15357, Jaggars Point NS 15358.
- Still out, each failing on something other than the minimum:
  - quality: Bayside LA, Campfire Cove KY, Paradise Citi AL
  - no published rate: Clearwater Ranch TX, Treasure Cove IN, Skycroft ON
  - size: Belle and Beau TN, Shady Oaks TX
  - mostly seasonal: Coolbreeze QC (5 of 126 traveller sites), Bell Haven ON (3 RV sites)

**Three skips had been misreads, not minimums:**
- Oscoda's Firefly '3 NIGHT MINIMUM' is for its Halloween festival weekend only.
- Cardinal's 2-night line is the cabins'.
- Tiny House's engine sells one night on its RV sites.

Lesson: read what the minimum is attached to (cabins, events, holidays) before calling it standing.

**AWH's answers (2026-10-12):**
- Domaine du Lac Libby restored as 15359. The engine asks 2 nights on every site opened for June and July 2027 weeknights, so the minimum is marked.
- American Way WV left out (4-night minimum).
- Goethe 14396 dropped ($75-80, over the gate) and Péninsule 15355 dropped (mostly seasonal). Netley Creek 15357 kept.
- Not answered, so still `ask` rows: the four 10-01 removals that are also over the $50 gate (Five Branches CO, Davidson's NH, Sentinel Oaks TX, River Rock PA). They stay out unless AWH says otherwise.
- Removals are logged in `audit/minimum_stay_reopen/dropped.jsonl`; `apply.py` now has `drop` and `minimum` verdicts.

**AWH's second round (2026-10-12), two calls left to me:**
- The Landing on Red Gut Bay came back as 15360 (`restore` row with `removed_how`): the rates page archived 2023-11-30 put its '4 Day minimum charge' under the '2023 Cabin Rates' heading; campsites are C$50 a day.
- South Bay Resort ON (12704) dropped as mostly seasonal, not for its minimum: its own homepage and reservation page say seasonal-only for 2023 and 2024 (25 seasonal spots, all reserved), and nothing newer exists (Facebook's newest public post 2024-01-08).
- Paradise Shores CA kept: its 5-night minimum covers only the 4th of July.
- Next id 15361.

**Follow-up DONE 2026-10-12** (`minimum` rows in decisions.json; 43 entries edited, each with a dated source read that day). The scan of notes naming a minimum without `booking.min_stay` found 59; it had also skipped about a dozen whose note mentioned an operating season near the minimum, and those were done too.
- Marked (min_stay + MINIMUM STAY line + booking.note, with any walk-up or waiver path): Silver Thread CO, Bison Ridge IA, Minong, Petenwell, North Bay Shore, Sidie Hollow and Esofea WI, Wabasis and Brower MI, Button Bay VT (waived inside 7 days), Ralph J Andrews NC, nine Go Camp Tennessee parks (2 nights; 'call the campground to request an exception'), Bates Beach BC and Granite Point WA (summer), Onoville NY (3 nights July-August), Jellystone NS, Bunker's WA, Jack Guthrie TX (3), Tolt-MacDonald WA, Fort Camping BC, Honeycomb AL, Scharnberg IA (3, first-come sites), Wilsonville PA, Paradise Shores CA (5 over July 4th, none same-day).
- Misreads, notes corrected: weekend or holiday rules read as standing (Driftwood IL, Rangeley and Peaks-Kenny ME, Chippewa MN, Nature's Hideaway AB, South Bay ON whose waterfront tier needs 7 nights in summer); booking lead times read as minimums (Metzler OR: book 3 days ahead; Twin Lakes WI: rec.gov 4-day cutoff); none found (Armitage OR); NY state parks reworded to the agency's '1-3 nights by park' with same-day bookings and walk-ins.
- Left alone: SC state parks (registry row carries the minimum and its waiver), cabin- or rental-only minimums, High Falls SC (waterfront sites only), Sandy Cove OK (event), Niagara Shores NY (busy-time lakeview sites), Zion OH (none).
- Not confirmed, notes unchanged: Loud Thunder IL (walk-ups exist), Oak Park CA and Otsego Lake MI (Itinio shows a human check), Hidden Valley Ranch NM, Blackhawk Lake WI (CampLife), Hoeft's WI, Elkhorn CO, Omaha Beach NE, Amishville IN.
