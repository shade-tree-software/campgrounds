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

Per-state decisions go in `audit/ridb_gap_<ST>_decisions.json`, recording added / excluded and *which kind of no* each was, so a later pass does not re-offer what was already judged. A caveat that is expected to lift (a closure) goes under `recheck` with the facility ids, so the note gets corrected rather than quietly going stale.

**A real campground with a problem gets an entry with the problem in the `note`** — see [[feedback_add_with_caveat_not_withhold]]. Only a genuine failure of the criteria is an exclusion; AR's single one was White Rock Mountain on the 20-ft size gate.

**Oregon (2026-09-22, 16 added ids 13185-13200, 7 excluded) added four rules:**
- **Check the rec.gov id before anything else.** 3 of OR's 23 rows (10 of 178 overall) were already entries whose `website` carried the same facility id; RIDB pins can be 150 km off, so the coordinate dedup missed them. `cited_facilities()` in the triage now does this.
- **Read the rec.gov `notices`** (`/api/camps/campgrounds/<id>`), not just the catalog: Eagle Creek (20-ft trailer limit on the road) and House Rock (trailers over 20 ft struggle) fail the size gate on ACCESS while their pads measure 65-120 ft. The notices also carry closures and ford crossings (Kinnikinnick).
- **"Proximity to Water" per-site attribute is a lead, not a verdict** — its value is often wrong ("Lakefront" on rivers) and at Indian Henry it meant a tributary creek. Measure each flagged pad to the OSM water line (Overpass, back off on 429) and apply the ~50 m bound: kept Cape Perpetua/Tollgate/Alsea/Still Creek, downgraded Clear Lake.
- **Bundle facilities** (John Day basin = 4 campgrounds, one id): one entry per loop, `sat_look.py <fid> --at <loop> --labels`; recgov_hookups skips shared ids, so hookups come from the note scan.

**The East (2026-09-22, 16 adds ids 13201-13216 from 33 rows) added:**
- **Horse camps hide as STANDARD sites.** Hoosier NF trailhead camps (Blackwell, Hickory Ridge, Shirley Creek, Youngs Creek), Station Camp and Cottonwood Patch all type their sites STANDARD NONELECTRIC; only the description (hitching racks, high-lines, troughs, "geared to provide for horses") gives them away. A mixed campground whose general loop is separate stays (Harmon Den lower loop).
- **Dispersed-site systems are one facility id over tens of miles** (Dale Hollow shoreline, AuSable River's 55 miles, Delta NF's forest roads) — no single pin describes them; excluded, Delta NF raised with AWH as a judgement.
- **Catalogs fill "Proximity to Water: N/A"** on every site (Saddle Lake) and some regions use a "WATERFRONT SITES" attribute instead — sat_look handles both.
- **The catalog's permitted-equipment list can be the size gate**: Katahdin's Sandbank Stream allows vans, pickup campers and pop-ups only.


**Hand-correcting a catalog-derived hookup needs `method: "reported"`** (2026-09-24). `recgov_hookups.py --apply` rewrites any `derived` hookups group from the catalog on every run, so Sandy Cove's (13241) water:false, set from a rec.gov notice that contradicts the catalog, was silently flipped back to true by the NEXT state's apply. Only `manual`/`reported` survive; stamp the correction `reported` with the notice named in `source`.
