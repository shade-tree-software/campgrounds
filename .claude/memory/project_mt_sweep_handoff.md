---
name: project_mt_sweep_handoff
description: "Montana sweep COMPLETE — all 4 add-buckets + waterfront audit done, committed & pushed (295 entries, ids 6054-6348)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 28dfddfb-bc19-4a4e-802d-8b193b941500
---

**Montana sweep — COMPLETE (2026-07-02).** All four ADD buckets and the waterfront audit are done, committed, and pushed to master. **295 new MT entries** (ids 6054-6348; +2 pre-existing Glacier NP Apgar/Many Glacier). Add-bucket ownership: federal 213, state 28, local 22, private 34.

**Waterfront audit — DONE (100%, 295/295 carry `waterfront_evidence`).** Ran the 251 water-adjacent entries through `audit/waterfront_audit_instructions.md` subagents in 32 batches (sequential, one at a time per [[feedback_sequential_sweep_agents]]), applied with `apply_waterfront_audit.py`, committed+pushed in 4 chunks (parts 1-4). Then stamped the 44 research-confirmed-dry ids (in-town RV parks / fairgrounds / badlands-upland / dispersed passes — satellite look skipped per the no-water-near exemption) with evidence in a final commit. Commits: "Audit MT waterfront batches 1-8/9-16/17-24/25-32 (part 1-4)" + "44 research-confirmed-dry entries".
- **105 upgrades** (every changed entry went from the `not waterfront` placeholder → an earned value): **60 on-water** (25 lakefront, 24 riverfront, 9 creekside, 2 pond) + **45 view** (25 lakeview, 20 riverview). **190 stayed not waterfront.** **10 coord fixes** (mis-pins repinned + elevation refreshed; e.g. Devil's Elbow, Bannack, Whitefish Lake, Drummond, Spring Gulch, Sloway, Marten Creek, South Van Houten, Barry's Landing).
- MT pattern held: reservoir drawdown sites earned on-water via open sand/grass aprons measured to high-water edge (Canyon Ferry White Sandy/Black Sandy/Silos/Confederate/White Earth, Koocanusa Peck Gulch, Hebgen Lonesomehurst/Cherry Creek/Wade, Hungry Horse Peter's Creek/Devil's Corkscrew, Cooney, Ackley, Afterbay). USACE/BLM river sites → riverfront (Madison Palisades/Red Mountain, Yellowstone Carbella/Itch-Kep-Pe, Missouri Judith Landing/Toston, Kootenai Yaak River/Dunn Creek Flats). Canopy-blind USFS creek/lake sites deferred to rec.gov/USFS per-site maps; most defaulted down (no per-site shoreline flag) but a few confirmed creekside (Basin, Cable Mtn, Dry Wolf, Jimmy Joe, Grizzly, Perrys) or on-water (Red Meadow Lake, Piney, Big Eddy). Glacier NP campgrounds all set back behind treelines → not waterfront.

**MT is fully done** — no legacy loose ends (fresh-state sweep, inclusion + waterfront folded into the add per current standard; `inclusion_evidence` was recorded at add time). Method identical to [[project_nd_sweep_handoff]] / [[project_sd_sweep_handoff]]. Reusable tmp artifacts were `/tmp/mt_wf_b*.json` (32 batch files w/ leads), `/tmp/mt_wf_dry_ids.json`+`_dry_info.json`, `/tmp/mt_wf_prompt.txt`, results in `/tmp/mt_wf_results/r*.json`, `/tmp/append_bucket_mt.py`.
