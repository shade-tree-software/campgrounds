---
name: reference_rvlife_price_cad
description: RV Life price_level $ tags are NOT currency-adjusted — CAD parks over-tiered vs USD; use CAD->USD converted rate for the affordable gate on Canadian sweeps
metadata: 
  node_type: memory
  type: reference
  originSessionId: e360afcf-a955-46e0-8838-fddebbc8d878
  modified: 2026-07-24T12:41:13.379Z
---

RV Life's `price_level` (0-4 $ signs) is bucketed from the raw nominal `avg_rate`
(nightly price) with FIXED thresholds — the $/$$/$$$/$$$$ cutoffs are $20 / $40 / $70,
**identical for the US and Canada, with NO CAD→USD conversion**. Verified 2026-07-23
by comparing a 794-park US sample (NY/VT/NH/MA/ME/CT) with 253 QC parks: both put the
$$/$$$ boundary at exactly $40 and $$$/$$$$ at $70/71. QC's $$$ median is $46 CAD
(≈ US$33) — if it were USD-converted it would read ~28% cheaper than the US; it
doesn't, proving `avg_rate` is raw local currency (CAD for Canada).

**Consequence:** Canadian parks are pushed up ~one price tier relative to their real
USD cost. The standard private-inclusion gate (RV Life `price_level` ≤ $$ AND
`star_rating` ≥ 4) therefore wrongly excludes genuinely affordable Canadian private
parks. In QC this dropped ~63 real $$ (USD-terms) ≥4★ campgrounds.

**Rule for all future Canada sweeps:** apply the affordable half of the private gate
on the **CAD→USD-converted** rate — i.e. keep private parks with `avg_rate` ≤ ~$55 CAD
(≈ $40 USD at ~0.72) AND `star_rating` ≥ 4 — NOT the raw RV Life $ tag. (Record the
original $ tag in the note as usual.) See [[reference_rvlife_price]] for the base
price-field mechanics and [[project_qc_sweep_handoff]] for the corrected-pass run.

The 5 Canadian provinces done before this finding (ON/BC/AB/SK/MB, per
[[reference_canada_sweep_adaptation]]) used the raw nominal gate and had
under-added private parks — the CAD-corrected private top-up there is now
**DONE** (2026-07-24, [[project_canada_cad_private_topup]]): 190 adds across
the 5 provinces (ON 84, BC 75, AB 26, SK 3, MB 2), waterfront-audited.
