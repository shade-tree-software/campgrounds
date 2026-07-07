---
name: project_tx_sweep_handoff
description: "Texas sweep IN PROGRESS — state/federal/local DONE+audited+committed (336 entries, ids 7009-7344); private bucket (797 candidates, ~100 batches) is all that remains"
metadata: 
  node_type: memory
  type: project
  originSessionId: e740b1a4-ad78-4aa2-a391-d333d567814c
---

**Texas sweep — IN PROGRESS (started 2026-07-03).** Fresh state (0 prior TX
entries). By far the largest sweep: **2,896 RV Life hits → ~1,220 candidates** across
4 ownership buckets. Method identical to [[project_la_sweep_handoff]] /
[[project_ok_sweep_handoff]] (both audits folded into the add per current standard).
New ids started at 7009.

**DONE + committed + both-audited (3 of 4 buckets, 336 entries, ids 7009-7344):**
- **State** (97 cand → 82 keeps, ids 7009-7090): TPWD parks + THC historic sites +
  LCRA/river-authority rec areas. Reserve via texasstateparks.reserveamerica.com.
  Waterfront: 36 upgrades (16 lakefront, 13 lakeview, 3 Gulf coastal dunes, 2
  riverfront, bayfront, bayview) + 8 coord fixes. Skips: walk-in/tent (Enchanted
  Rock, Government Canyon, Bentsen, Caprock tent units), day-use (Big Spring),
  backcountry (Devils River, Interior-Big Bend Ranch), closed/sold (Fairfield Lake),
  workforce (Tips), 20-ft cap (Colorado Bend), cabins/hike-in (Fort Boggy).
- **Federal** (144 cand → 106 keeps, ids 7091-7196): USACE reservoir parks dominate
  (rec.gov per-site SHORELINE/Lakefront flags = the key evidence; rec.gov per-site
  API `/api/camps/campgrounds/<id>/campsites` gives exact lat/lng to overlay on
  satellite) + NPS (Big Bend/Guadalupe Mtns/Padre Island/Amistad/Lake Meredith) +
  USFS forests/grasslands. Waterfront: 71 upgrades (45 lakefront) + 17 coord fixes.
  Skips: ~17 military FamCamps, tent-only/walk-in, equestrian (Ebenezer/TADRA),
  closed, umbrella/cross-batch dups (Malaquite, Lake McClellan). 2 LCRA→state, 1
  concessionaire→private.
- **Local** (183+10 cand → 148 keeps, ids 7197-7344): city/county/municipal-utility
  & WATER-DISTRICT parks (no star/price gate for local gov). Waterfront: 51 upgrades
  (20 lakefront, 4 Gulf coastal dunes, 3 bayfront, 2 pond) + 2 coord fixes. Skips:
  private-mis-tags below gate, workforce/oilfield & residential-monthly, event-only
  fairgrounds (Fair Park/Fannin), day-use, tent-only, camping-banned/closed, group-
  only. Reclassed: 5 private (pass gate), 3 river-authority→state (LCRA/Brazos/
  Trinity), 1 BuRec→federal. **Ownership rule settled: municipal/regional WATER
  DISTRICTS (CRMWD etc.) = local; true RIVER AUTHORITIES (LCRA, Brazos RA, GBRA,
  Sabine RA, Trinity RA) = state.**

**IN PROGRESS: private bucket** — 797 gated candidates (commercial with RV Life
price_level<=2 & star_rating>=4), ~100 batches of 8. Split files staged at
`/tmp/tx_private_batch_*.json`. Vet each per inclusion (skip membership/Thousand-
Trails/Encore, Elks/Moose lodges, casino lots, 55+/seasonal Winter-Texan, residential-
MH, workforce/oilfield monthly/long-term — COMMON in Permian Basin & Eagle Ford & RGV;
dead-website+thin-reviews strike). Keep rate ~75%.
- **RESEARCH COMPLETE: all 100 batches done -> 586 private entries added+committed+pushed in 12 chunks (ids 7345-7930).** Reclassed along the way: several LCRA/GBRA/LNRA river-authority -> state (incl Lake Bastrop South Shore), USACE -> federal, county/city -> local (Harper Park, Harris St, I.B. Magee, Lake Hawkins, Magnolia Beach, Pleasure Island, Ray & Donna West, Rising Star, San Saba River, W. Lee Colburn/Winters, Waylon Jennings/Littlefield, Wichita Bend/Wichita Falls). Mission Dolores -> THC/state. Dropped cross-bucket/cross-batch dups: Overlook Park (=federal 7153), Lighthouse RV Park (=North Point Landing), Magnolia Beach Camping, Bayside, Lone Star Resort. Keep rate ~65% (heavy 55+/RGV-Winter-Texan, Permian/Eagle-Ford workforce, Thousand Trails/Encore/Patriot chains, long-term/MH in the P-Y alphabet).
- **NOW IN PROGRESS: the deferred WHOLE-private-bucket waterfront audit.** Built via
  `build_wf_batches.py privatewf 7345 7930` (leads copied to `/tmp/tx_leads_privatewf.json`):
  586 -> 153 auto-dry (stamped not-waterfront in `/tmp/tx_wf_auto_privatewf.json`) + 433
  to audit. Re-chunked the 433 into **29 batches of 15** at `/tmp/tx_wf_privatewf_batch_<n>.json`.
  Running `audit/waterfront_audit_instructions.md` agents SEQUENTIALLY, results ->
  `/tmp/tx_results/wf_private_<n>.json`. **NEXT after all 29:** concatenate the 29 result
  files + `/tmp/tx_wf_auto_privatewf.json` into one results array and apply with
  `python3 audit/apply_waterfront_audit.py <results.json>` (sets waterfront, coord fixes,
  writes waterfront_evidence), commit, push, then **mark TX COMPLETE**. If `/tmp` cleared,
  rebuild leads are gone but the audit can re-discover per-entry from each entry's `location`.

**Reusable plumbing (all in /tmp, recreate if session lost):** `pull_tx.py`
(Algolia app H0LPZK92QJ, key inline in any park page HTML), `bucketize_tx.py`,
`split_tx.py <bucket> 8`, `append_tx.py <ownership> <results...>` (assigns ids from
max+1, stamps state=TX + per-record ownership, saves id->lead map to
`/tmp/tx_leads_<ownership>.json`), `build_wf_batches.py <bucket> <lo> <hi>` (auto-
stamps dry entries, splits rest into wf batches carrying leads), `tx_addendum.md`
(TX authorities: state/federal/local sections). Research results in
`/tmp/tx_results/<bucket>_<n>.json`, wf results `/tmp/tx_results/wf_<bucket>_<n>.json`.
Run agents SEQUENTIALLY one at a time per [[feedback_sequential_sweep_agents]].
**Watch for cross-batch duplicates** — dedup by coord proximity (<0.5km) before
append (found 2 in federal, 2 in local). Open-Meteo elevation API is UNREACHABLE
from this sandbox's shell/WebFetch — a few coord-fixed entries kept old elevations
(negligible on flat terrain); subagents CAN reach it.

See [[reference_rvlife_price]], [[reference_local_campground_method]],
[[feedback_waterfront_evidence_in_json]], [[reference_inclusion_audit]],
[[feedback_campground_vetting_discipline]].
