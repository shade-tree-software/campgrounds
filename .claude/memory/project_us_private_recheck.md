---
name: project-us-private-recheck
description: "2026-10-12 re-check of the 125 US private-gap parks admitted without a rate read on their own site; 3 removals proposed and waiting on AWH (Harmony Ridge members-only, Dunham's permanently closed, Lakeview TX no rate); tools in audit/us_private_recheck/"
metadata:
  type: project
---

**Done 2026-10-12, commit e18fdee (not pushed when written).** The Canada re-check ([[project-canada-private-recheck]]) pointed at the US: the 125 private-gap entries (ids 14201-14937) whose inclusion_evidence had no dollar figure, i.e. admitted on RV Life's tier, a Google listing or an unread operator page. Record: `audit/us_private_recheck/` (ids.json, scan.py with rate/age/login/monthly signals, scan_2026-10-12.json, decisions.json, apply.py). Progress lives in the data: `re-check 2026-10-12:` in inclusion_evidence.

**Waiting on AWH (drop_proposed, nothing removed):** Harmony Ridge Resort CA 14916 ('Our members-only, family resort', every member screened, free first stay for prospects); Dunham's RV Park KS 14546 (Google 'Permanently closed', not so on 2026-10-02); Lakeview RV Park TX 14784 (RV Life $ with no average rate = default tier, no website, only dated price a 2021 Campendium $25; phone 903-854-4712 or 951-404-4446 could settle it).

**Written:** AGE-RESTRICTED lines on 13 parks whose own pages say 55+ (7 RGV Encore resorts say 'Age Qualified'; the FL Encore ones and Foothill Village AZ are all-ages); Lake Joy WI standing 2-night minimum marked; Grape Hammock FL nightly = $16 rustic W/E sites, full hookups leased yearly; dead websites removed (Ardmore OK domain now forwards to a scam download page; Cypress Isle FL Facebook gone); caveats on Brixey Lake OK and Heritage KS; Chiriaco Summit CA camper-reported free (Campendium Jan 2026).

**Lessons:** the Encore template names everything (55+, login, monthly, sold), so its scan flags are noise: read each resort's own 'Age Qualified' line. Encore's Newbook shows rates logged out ('No Membership Needed to Book'). Three minimum-stay hits were cabins' (Lake Champlain, Lighthouse) or holidays' (Arbuckle). gm.py launches its own Chrome, so with the driver running use the driver for Google Maps; the reviews-sort control doesn't respond to scripted clicks, so read the freshest age among the first reviews. A RV Life avg_rate of 0 or 1 is not a real tier.

Related: [[project_private_gap]], [[feedback_minimum_stay]], [[feedback_camper_report_rates]].
