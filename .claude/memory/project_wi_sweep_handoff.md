---
name: project_wi_sweep_handoff
description: "WI COMPLETE — waterfront 100% AND inclusion 100% (345/345, no loose ends). 2026-07-21 the residual 165 waterfront entries were inclusion-audited: 162 keeps, 3 removed (Mineral Lake decommissioned, Island Camping seasonal-only, Seagull Marina too-many-strikes/owner call)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4cef485f-82b3-4807-8ce0-23e58b9248fa
  modified: 2026-07-21T22:47:49.098Z
---

WI waterfront audit is now **100% (348/348)** — every WI campground carries a `waterfront_evidence` string. The final 113 unaudited not-waterfront entries were swept 2026-06-26 (commit bc98165): 7 upgrades (Anvil Lake/West Point/Hoeft's → lakefront, Hi-Pines → pond, Big Bay SP → coastal woods on Lake Superior, Ottawa Lake + Yellowstone Lake → lakeview), 2 coord fixes (Hartman Creek 3276, South Trout Lake 3303). The earlier 70 were audited before this session.

WI **inclusion** audit is now **COMPLETE (2026-07-21)**. The residual 165
currently-waterfront entries (81 local, 32 state, 32 federal, 20 private) were
audited in 21 sequential batches of 8: **162 keeps stamped, 3 removed, 0 open
reviews.** WI went 348 -> 345 campgrounds.
- **Removed:** 3345 Mineral Lake (Chequamegon NF — USFS decommissioned it,
  toilets removed + entrance barricaded, day-use boat landing only now, per
  apg-wi Ashland Daily Press; rec.gov 234093 "currently closed"); 3392 Island
  Camping & Marina, Stockholm (seasonal/members-only, "they don't do nightly");
  3441 Seagull Marina, Two Rivers (audit flagged review — website "Closed for
  the Season" + for sale, mostly seasonal — and the OWNER decided remove: too
  many strikes, ambiguous status + next to a sewage treatment plant in a largely
  urban stretch). None had trip_data refs.
- The heavy local bucket (81 county/town/village parks) was almost all clean
  keeps — WI county/municipal parks are legit transient RV campgrounds with
  county-gov reservation portals. The only removes were 1 federal + 2 private.

Per [[reference_inclusion_audit]] and [[feedback_waterfront_evidence_in_json]].
Remaining legacy-inclusion backfills (waterfront done, inclusion pending on
currently-waterfront entries): NY ~89, NE ~80, IL ~64, TN ~63, IN ~33, IA ~40.
