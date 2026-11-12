# Resuming phase 7 in Minnesota (saved 2026-11-11, stopped by AWH after p3-437)

Applied through **p3-445** (the unread sweep: 5705 read, 5576 Spafford DROPPED, 9 still unread = phone list in MN_NOTES_p3-445.md, calls wait for AWH). Next: vet the MN leads below, then North Dakota. Next new id **15671** (15669 Shell City Landing, 15670 Fury's Island added from the leads).
Pushed through 15520ad1 (p3-437); deploy not confirmed. ONE verifier at a time.

## Build a batch (from the repo root; SCRATCH = the new session's scratchpad)

    python3 -I audit/verify/queue.py --batch p3-444 --state MN --limit 11
    python3 -I audit/verify/kit/mn/mkpara_mn.py $SCRATCH p3-444
    python3 -I audit/verify/kit/mkbrief_mo.py $SCRATCH p3-444 $SCRATCH/p3-444_para.txt
    mkdir -p $SCRATCH/p3-444 && cp -r audit/verify/kit/mn/tools $SCRATCH/p3-444/tools

Then launch ONE background general-purpose agent with `agent_prompt_template.txt`
(replace SCRATCH, p3-NNN and the id list; the brief may say "twelve", the batch has eleven).
`last_brief_p3-437.txt` is the last generated brief, for reference.

## Apply a batch

1. Dropped/unread results -> `$SCRATCH/p3-N/<id>.dropped.json` / `.unread.json` (no result file = unread).
2. `python3 -I audit/verify/apply.py <ids> --apply` (writes no phone, website, waterfront or pin).
3. Post script with asserting helpers: `pin` (+ Open-Meteo elevation), `ph`, `web`, `wf`
   (asserts no --AWH; appends `p3-N (date): ...` to waterfront_evidence), `cn` (curation_note line
   `p3-N (date): ... --Claude`). Dump with `ensure_ascii=False, indent=2` + trailing newline.
4. Drops: DROPS dict in audit/verify/criteria_drops.py, then `--apply` (no `\$` in the text).
5. Tests: `python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`.
6. Copy MN_NOTES_p3-N.md here; append criteria_followups.md + waterfront_leads.md; update the
   chain in .claude/memory/project_phase7_verification.md; commit with explicit paths incl.
   audit/verify/results/applied/<id>.json (never `git add audit/verify/` wholesale).

## Left for the end of Minnesota

- **Unread sweep** (queue.py never re-issues ids sitting in a batch file, so these need a manual
  batch): 5518 Bray Park, 5669 Moose Lake City, 5576 Spafford (seasonal-only concern),
  5633 Gilbert Olson (proposal riverfront -> creekside; earlier read was a Wayback copy = unread),
  5651 Lake Allie County Park (Renville County Cloudflare + ResNexus Incapsula, p3-438),
  13327 Sebeka City Park (cityofsebeka.org Cloudflare, p3-441),
  Cloudflare-refused city sites 5649 Karlstad, 5689 Sherin, 5702 Warroad, 5705 Wildcat (its Firefly
  portal is readable), 13342 J.F. Jacobson Park (Madison), 5694 Sunnybrook.
- **Leads to vet:** Shell City Landing Campground (DNR cmp00027, 46.791808,-94.948024, Huntersville SF; p3-441), Fury's Island County Park (Nobles County, ~1 mi S of Maka-Oicu 13332; p3-439), Red Pine Campground (Saginaw), Horseshoe Park (Hallock; find a non-refusing
  source), Snake River Campground (Aitkin County, south of McGrath).
- **Open questions** are in audit/verify/criteria_followups.md (p3-428 .. p3-437 sections).

## After Minnesota

AWH 2026-11-11: "After Minnesota, do North Dakota, then Illinois." (Then the other 33 Vermont
entries - `queue.py --state VT`, kit in audit/verify/kit/vt/ - AWH: "After Illinois".)
ND and IL need their own brief header (model on kit/mn/mn_head.txt).
