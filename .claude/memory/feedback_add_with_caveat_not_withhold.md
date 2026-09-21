---
name: feedback_add_with_caveat_not_withhold
description: A real campground that is closed or under-documented gets an entry with the caveat written into the note — don't withhold it
metadata:
  type: feedback
---

AWH 2026-09-21, on the first federal-gap state: three Arkansas campgrounds had been withheld — two closed (Lake Wedington, infrastructure damage; Notrebes Bend) and one whose max RV length neither rec.gov nor the RIDB catalog publishes (Blue Ridge Park) — and the instruction was to **add all three with the caveat in the note**.

**Why:** an entry carrying a warning is more use than a campground that is invisible. A withheld campground is indistinguishable from one that was never found, so the work of judging it is lost and the next pass pays for it again. A closure lifts; an unconfirmed site length is a phone call. Neither is the campground failing the criteria.

**How to apply:** put the caveat where a reader meets it — in the `note`, in plain words, dated ("CLOSED as of Sept 2026", "site length unconfirmed … ring the project office"), and name the next action. Repeat it in `inclusion_evidence` so the audit record doesn't read as a clean pass. Track a caveat that should lift under `recheck` in the state's decisions file so the note gets corrected rather than going stale.

**What still excludes:** a genuine failure of the inclusion criteria — the 20-ft size gate ([[feedback_min_site_length]]), no RV sites at all, no live web presence ([[feedback_require_live_web_presence]]), seasonal/residential/membership ([[feedback_exclude_seasonal_residential]]). "Closed this season" and "not documented" are not that.

This is the same instinct as [[feedback_absent_is_not_unknown]] one level up: don't let a missing fact delete the thing the fact was about. Related: [[reference_ridb_gap_pipeline]], [[feedback_campground_vetting_discipline]] (which still governs — the caveat is not a licence to add an unvetted entry).
