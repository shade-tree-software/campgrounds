---
name: reference_ridb_gap_pipeline
description: How to work the 585-row federal gap list — triage by RIDB's campsite catalog first, then break the canopy deadlock by plotting per-site coordinates on satellite imagery
metadata:
  type: reference
---

Two tools turn [[reference_rvlife_index_has_gaps]]' 585 candidates into real entries. Both were built and proved on Arkansas, 2026-09-21 (9 added, ids 13158–13166).

**`audit/ridb_gap_triage.py` — sort before you sweep.** Fetches `facilities/<id>?full=true` (agency, real state, phone, fee, description) and `facilities/<id>/campsites` per row, then verdicts each with `recgov_hookups.rv_sites` unchanged. Only **one** of five verdicts is a drop:

- `likely_rv` — 3+ RV-capable sites: the work list
- `no_rv` — a real PUBLIC catalog with no RV site: tent/cabin/equestrian/boat-in
- `mgmt_only` — the catalog is only the agency's internal MANAGEMENT rows (Houston RA: 75 of them, 0 public). Says nothing about the campground
- `thin` — under 3 sites, in practice a lone group picnic shelter at a day-use park
- `no_catalog` — no per-site data, common for FCFS federal campgrounds

The last three are all kinds of *unknown* and are kept apart on purpose — fold any of them into `no_rv` and you drop campgrounds on the strength of a catalog that never described them ([[feedback_absent_is_not_unknown]]). Cache is `trip_data/ridb_gap_cache.json` (gitignored, keeps EVERY campsite attribute, deliberately NOT `recgov_hookups`' own cache). `--limit` caps a run, SIGINT finishes the facility in flight, `--report` is free ([[feedback_chunked_bulk_passes]]).

**Three things the catalog decides for free**, which normally cost manual research:
- **the 23-ft size gate** — per-site `Max Vehicle Length`/`Driveway Length`. White Rock Mountain and Boulder Basin both cap at 20 ft and would have been bad adds ([[feedback_min_site_length]])
- **currently-operating** — "RV sites, none bookable" caught Notrebes Bend as closed before the web page confirmed it
- **`inclusion_evidence`** — the per-site catalog IS the authoritative per-site source the inclusion rule asks for

**`audit/sat_look.py` — plot the pads, don't squint at the trees.** The waterfront gate makes the satellite look mandatory but forbids a canopy-blind look from downgrading, and most federal campgrounds in this list are exactly that (not one of Cowhide Cove's 47 pads resolves). RIDB's catalog carries **each campsite's own coordinate** — per-site agency data, the authority the gate already defers to when canopy wins — so plotting them on stitched Esri World Imagery with a scale bar makes the ~50 m distance bound *measured*. `python3 audit/sat_look.py <facility_id> -z 17` (z18 `--span 1` to settle a close call), then read it with the Read tool.

A dot is a pad, not a verdict — the buffer still has to be read off the image, and doing so is what produced AR's three honest downgrades: Hill Creek (a marina road between every pad and the water → `lakeview`), Wilbur D. Mills (45–65 m behind a bank road → `riverview`), Quarry Cove (imagery at flood pool, so the normal high-water apron cannot be read at all → `lakeview`).

**Leave `hookups` unset on the new entries.** `recgov_hookups.py` fills them from this same catalog under its own provenance and walk-up rules — the right seam ([[feedback_lone_electric_site_may_be_host]]).

Per-state decisions go in `audit/ridb_gap_<ST>_decisions.json`, recording added / excluded / **held** and *which kind of no* each was, so a later pass does not re-offer what was already judged. Blue Ridge Park (AR) is the worked "held": a real-looking Dierks Lake loop whose catalog states no length and no permitted equipment, so it waits on a call to the project office instead of being guessed either way.
