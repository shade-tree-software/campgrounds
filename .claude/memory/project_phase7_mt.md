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

**Progress:** mt-1..mt-18 applied (mt-19 running). Dropped so far: 6166 B&L (presence), 6227 Grizzly (motorhomes not recommended), 6168 Sand Springs (dead site), 6136 50,000 Silver Dollar (casino/truck-stop lot), 6158 Rivers Bend (presence), 6135 Canyon RV (dead site), 15380 Aspenwood (RV Life $$$, no price indicator), 6153 Happy Camper (site was a Texas park), 6133 Perrys (price gate). 15368 Leaning Tree -> hipcamp. 6071 Homestake Pass + 6159 Kiwanis (AWH: lack of information), 6121 Jaycee West (no evidence camping allowed). 6118 Chester City Park (AWH: lack of information, town park with no official page). 6113 Tri-County Fairgrounds + 6193 Barretts Park + 6092 Sanford Park (AWH: lack of information). 14104 Arod Lake FAS (AWH: FWP says limited RV access). AWH kept 14595 Big Sky: a park selling nights on half its sites is not long-stay. 6165 Gods Country -> hipcamp. bw.py here must point at /opt/pw-browsers/chromium-1194 (pip playwright wants a newer build); USACE nws.usace.army.mil pages 403 from the cloud.

**Concurrency (AWH 2026-10-22):** this session runs its own single verifier beside the main session's; that is fine ("one thread only" is per session). Apply batch N before launching N+1.

**Main-session side (merged 2026-10-22, session f407aa47):** the local session skips MT and fetches + merges origin/master before pushing. On the first merge the MT side's criteria_drops.py carried back the 4241 Country Woods / 4253 Ho-Hum drop lines, restored in e311c27a (both entries still in campgrounds.json): re-running `criteria_drops.py --apply` would have dropped them again. Merge resolution dropped those two lines; when resolving DROPS conflicts, keep both sides but never re-add a line for an entry that is still in campgrounds.json.

**LESSON (2026-10-22): 'no posted nightly rate' is NOT a drop for an ordinary private park.** Test 2 binds only long-stay parks; otherwise a working website + phone (or Google 25+ reviews + phone) plus an RV Life $/$$ passes. I wrongly dropped 6148 Hyde and 6155 Riverside and restored them. Before a presence/price drop: check rating.price_tier and Google Maps (bw.py on google.com/maps/search/<name+town>).
