---
name: project-minimum-stay-reopen
description: "2026-10-11 re-open of everything the 2026-10-01 standing-minimum rule removed or skipped: 17 added/restored + 2 re-adds marked (ids 15342-15358), 10 still out on other grounds, 7 questions for AWH; next id 15359"
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

**Waiting on AWH (decisions.json `ask` rows):**
- Restore Domaine du Lac Libby? AWH dropped it on 10-09, the day before the rule changed.
- American Way WV has a 4-night minimum.
- Restore four 10-01 removals that are also over the $50 gate? Five Branches CO, Davidson's NH, Sentinel Oaks TX, River Rock PA.
- Keep Goethe 14396 at $75-80?
- Borderline seasonal adds he may want to drop: Péninsule (share not counted) and Netley Creek (77 of ~115 sites seasonal).

**Follow-up not done:** 59 existing entries mention an unscoped minimum in their note but carry no `booking.min_stay`. Many are fine as they are: SC state parks and the Go Camp Tennessee sites waive it by phone, and some minimums apply only to cabins. The rest are worth marking: Bison Ridge IA, Minong WI, Metzler and Armitage OR, Oak Park CA, Chippewa MN, Esofea WI, Jellystone NS, Alcona MI (5 nights in summer, ask), The Landing on Red Gut Bay ON (4 nights, ask). Find them with the regex scan in this session's notes, or grep notes for "night min".
