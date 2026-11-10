---
name: feedback-look-up-before-asking
description: A keep/drop question that one easy lookup would settle is looked up, not asked; ask AWH only when completely stuck
metadata:
  type: feedback
---

AWH 2026-11-10: "if you have a campground like Fort Macleod Lions Club Campground which would be a keeper if you had an additional piece of information, and if that information is something you can easily look up, go ahead and look it up. No need to ask me unless you are completely stuck."

**Why:** I asked whether to keep or drop 9025 (no operator page, no posted rate) when the deciding fact - its RV Life price tier - was one index query away, and was already stored on the entry's `rating` group.

**How to apply:** before writing a keep/drop ask, list which rule would settle it and what fact that rule needs, then fetch it: the entry's own stored `rating` (RV Life tier/stars), RV Life's Algolia index ([[reference_rvlife_price]]), Google reviews count + phone, Good Sam ([[reference_good_sam_ratings]]), `audit/price_research/gateways.py`, a booking-engine probe. Decide by the rule and report the outcome in the batch summary. Verifier briefs should say the same (check the stored `rating` and RV Life before flagging presence/price). Asks remain for real judgement calls (rule doesn't cover it, sources conflict, --AWH values) - my reading of "completely stuck". See [[feedback_vet_new_leads_myself]], [[feedback_require_live_web_presence]].
