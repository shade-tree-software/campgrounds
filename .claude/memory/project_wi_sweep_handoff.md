---
name: project_wi_sweep_handoff
description: "WI COMPLETE — waterfront 100% AND inclusion 100% (345/346, 1 open review: 3441 Seagull Marina). 2026-07-21 the residual 165 waterfront entries were inclusion-audited: 162 keeps, 2 removed (Mineral Lake decommissioned, Island Camping seasonal-only)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4cef485f-82b3-4807-8ce0-23e58b9248fa
  modified: 2026-07-21T22:29:04.946Z
---

WI waterfront audit is now **100% (348/348)** — every WI campground carries a `waterfront_evidence` string. The final 113 unaudited not-waterfront entries were swept 2026-06-26 (commit bc98165): 7 upgrades (Anvil Lake/West Point/Hoeft's → lakefront, Hi-Pines → pond, Big Bay SP → coastal woods on Lake Superior, Ottawa Lake + Yellowstone Lake → lakeview), 2 coord fixes (Hartman Creek 3276, South Trout Lake 3303). The earlier 70 were audited before this session.

WI **inclusion** audit is now **COMPLETE (2026-07-21)**. The residual 165
currently-waterfront entries (81 local, 32 state, 32 federal, 20 private) were
audited in 21 sequential batches of 8: **162 keeps stamped, 2 removed, 1 open
review.** WI went 348 -> 346 campgrounds.
- **Removed:** 3345 Mineral Lake (Chequamegon NF — USFS decommissioned it,
  toilets removed + entrance barricaded, day-use boat landing only now, per
  apg-wi Ashland Daily Press; rec.gov 234093 "currently closed"); 3392 Island
  Camping & Marina, Stockholm (seasonal/members-only, "they don't do nightly").
- **Open review (still unstamped):** 3441 Seagull Marina & Campground — website
  shows "Closed for the Season" (in July) + "for sale" via First Anderson Real
  Estate, note says "mostly seasonal campers", BUT historically 100 waterfront
  RV/tent sites. Genuinely ambiguous current operating status; left for the
  owner to make the call (do NOT excise on this evidence). No trip_data refs.
- The heavy local bucket (81 county/town/village parks) was almost all clean
  keeps — WI county/municipal parks are legit transient RV campgrounds with
  county-gov reservation portals. The only removes were 1 federal + 1 private.

Per [[reference_inclusion_audit]] and [[feedback_waterfront_evidence_in_json]].
Remaining legacy-inclusion backfills (waterfront done, inclusion pending on
currently-waterfront entries): NY ~89, NE ~80, IL ~64, TN ~63, IN ~33, IA ~40.
