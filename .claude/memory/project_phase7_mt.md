---
name: project-phase7-mt
description: Phase 7 MONTANA run in a cloud session (2026-10-22), parallel to the main phase-7 session; batches mt-N on branch claude/youthful-ramanujan-3k9rmh
metadata:
  type: project
---

AWH 2026-10-22: a second (cloud) session works phase 7 on MONTANA only, beside the main session
([[project-phase7-verification]]), to spend expiring credits. Batches are named `mt-N` (never
p3-N) and come from `queue.py --state MT`. One verifier at a time in this session.

**Conflict rules:** MT notes in waterfront_leads.md / criteria_followups.md go in a
"## Montana (mt-N batches)" section near the TOP (the main session appends at the end), so
merges don't collide. removals.json will conflict on merge: keep both sides.

**Cloud-checkout gaps:** trip_data/trips.json is an empty placeholder (gitignored, family data
not here), but AWH 2026-10-22: "We have never stayed anywhere in Montana", so standing-rule drops
(presence, 4WD/motorhome-not-recommended, price gate with no gateway) go straight into
criteria_drops.py (MT block at the TOP of DROPS) and are reported. No RIDB key: helper catx.py reads rec.gov's
public search API for the per-site catalog. No PA deploy from here.

**Progress:** mt-1..mt-29 applied (mt-30 running). Dropped so far: 6166 B&L (presence), 6227 Grizzly (motorhomes not recommended), 6168 Sand Springs (dead site), 6136 50,000 Silver Dollar (casino/truck-stop lot), 6158 Rivers Bend (presence), 6135 Canyon RV (dead site), 15380 Aspenwood (RV Life $$$, no price indicator), 6153 Happy Camper (site was a Texas park), 6133 Perrys (price gate). 15368 Leaning Tree -> hipcamp. 6071 Homestake Pass + 6159 Kiwanis (AWH: lack of information), 6121 Jaycee West (no evidence camping allowed). 6113 Tri-County Fairgrounds (AWH: lack of information; Google shows only rodeo/4-H reviews, no camping). 6193 Barretts Park, 6092 Sanford Park and 6118 Chester City Park were dropped for lack of information, then RESTORED 2026-10-22 on a Google Maps check. 14104 Arod Lake FAS (AWH: FWP says limited RV access). 6308 Bitterroot Flat + 6320 Dalles (FS: motorhomes not recommended, Rock Creek Rd #102).  6257 Missoula Lake (fails the public no-web-presence ladder). 6335 Hick's Park (closure order + trailers not recommended), 13308 Howard Lake (20-ft trailer max), 6102 Matthews (AWH: parking-lot camping at a day-use site is not a campground). AWH kept 14139 Maidenrock (FWP "steep access road" is not a rig restriction). 14155 Prickly Pear FAS (rig-length rule: FWP "Very tight spot", reviews advise against RVs). 6281 Norton (AWH: walk-in sites per reviewers, FS silent). 6285 Schumaker (FS recommends high clearance on Lost Horse Rd). AWH kept 6284 Sage Creek: an agency-named camper route (from the south) with no clearance warning is enough; the note says which route to take. 14163 Spite Hill FAS (rig-length rule: FWP "Limited access for trailers and RV's", only rig review is from 2021). 6293 Timberlane (AWH: effectively group-only, closed 2026). 14164 Stuart Mill Bay season fixed (AWH OK). AWH kept 14595 Big Sky: a park selling nights on half its sites is not long-stay. 6165 Gods Country -> hipcamp. bw.py here must point at /opt/pw-browsers/chromium-1194 (pip playwright wants a newer build); USACE nws.usace.army.mil pages 403 from the cloud.

**Concurrency (AWH 2026-10-22):** this session runs its own single verifier beside the main session's; that is fine ("one thread only" is per session). Apply batch N before launching N+1.

**Main-session side (merged 2026-10-22, session f407aa47):** the local session skips MT and fetches + merges origin/master before pushing. On the first merge the MT side's criteria_drops.py carried back the 4241 Country Woods / 4253 Ho-Hum drop lines, restored in e311c27a (both entries still in campgrounds.json): re-running `criteria_drops.py --apply` would have dropped them again. Merge resolution dropped those two lines; when resolving DROPS conflicts, keep both sides but never re-add a line for an entry that is still in campgrounds.json.

**LESSON (2026-10-22): 'no posted nightly rate' is NOT a drop for an ordinary private park.** Test 2 binds only long-stay parks; otherwise a working website + phone (or Google 25+ reviews + phone) plus an RV Life $/$$ passes. I wrongly dropped 6148 Hyde and 6155 Riverside and restored them. Before a presence/price drop: check rating.price_tier and Google Maps (bw.py on google.com/maps/search/<name+town>).

**Public no-web-presence rule (AWH 2026-10-22, still forming):** a public campground with no agency/town page is kept if Google Maps lists it as a campground with a phone (add a note: call that number to confirm it is open), or a recent Google review confirms overnight camping (review count doesn't matter). Restored on that basis: 6193 Barretts Park (100 reviews, phone), 6092 Sanford Park (campground + phone, call-first note), 6118 Chester City Park (2 reviews, one 2 months old confirming camping). Club-run parks (6159 Kiwanis) fall under the private rule. Dispersed areas still need an agency designation (6071 stays dropped). Before dropping a public entry for lack of information, check Google Maps first.

**Official tourism sites count (AWH 2026-10-22; widened from Visit Montana to any official tourism website):** a state tourism office or government-designated tourism region / visitor bureau listing that describes a public campground in detail stands in as its official page when no agency page exists (Sanford Park's does). The verifier brief (scratchpad brief_base.txt) carries this and the Google Maps check. Searched for 6113 Tri-County Fairgrounds and 6159 Kiwanis: no Visit Montana page; Southwest Montana's fairgrounds listing now returns a server error.

**Rig length from reviews (AWH 2026-10-22):** a reviewer's rig length never goes into max_rig_ft. Agency silent on length -> keep, with a dated, attributed note caveat when a review from the last 3 years reports the reviewer's own 23-ft+ rig fitting. Agency vague ("small trailers only", "limited access for RVs") -> such a review settles it as a keep; none -> drop (14104 Arod Lake, 6325 Ekalaka Park). Agency explicit ("motorhomes/large RVs not recommended", 4WD, high clearance) -> drop whatever reviews say. In brief_base.txt from mt-24 on.

The public no-web-presence ladder and the rig-length-from-reviews rule are now in docs/campground-curation.md (AWH agreed 2026-10-22), so both sessions follow them.
