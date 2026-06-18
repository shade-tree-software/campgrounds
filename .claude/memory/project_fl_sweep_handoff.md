---
name: project_fl_sweep_handoff
description: "Florida campground sweep progress + handoff (state/federal done, private in progress, local pending)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9c3ecf0d-e001-42b3-a4d9-3445be29beb8
---

State-by-state Florida sweep status as of 2026-06-17 (machine move mid-sweep). Git log is the authoritative progress record; this captures non-git working state that would otherwise be lost.

**DONE + committed:**
- FL **state** stage — commit `c3638a2`: added ids 4700–4730 (31 entries: state parks + Florida Forest Service state forests + FWC WMAs), waterfront-audited.
- FL **federal** stage — commit `988c395`: added ids 4731–4743 (13 entries: USFS Ocala/Apalachicola/Osceola NF + NPS Long Pine Key & Bear Island), waterfront-audited. USACE had nothing new. Also reclassified 3 entries mislabeled federal→state: **101 Cary State Forest, 156 Ross Prairie, 166 Holder Mine** (Florida Forest Service state forests).

**DONE + committed:**
- FL **private** stage — commit `f73e9c1`: added ids 4744–4806 (63 entries: Panhandle/Big Bend, North Peninsula, Central, + the 3 South Okeechobee candidates), waterfront-audited in the same commit. 11 on-water (Sunset Isle bayfront; Astor Landing + Tampa South riverfront; LeLynn + Lake Toho + Bud's lakefront; Dead Lakes RV, Unhitched Leisure Lakes, Cody's Catfish, Little Flamingo, Cedars Lake pond), 4 view-only, 48 not waterfront; 5 coord fixes.
  - FL **age-restricted private** — commit `eec47e5`: added ids 4807–4812 (the 6 age-restricted parks initially excluded), per AWH's decision to keep them but state the age cutoff prominently. Each note leads with `AGE-RESTRICTED: <cutoff>` so the include/exclude call can be made per-trip by party composition: Southern Oaks (55+), International RV (55+), Floridian (18+), Lynch's Landing (adults-only renters), Scottish Traveler (18+), Travel World (21+). Waterfront-audited (5 not waterfront; Lynch's Landing riverview). **Convention going forward: don't auto-exclude age-restricted parks — add them with the age cutoff noted.** Find Out Farms stays excluded (unrated Hipcamp farm, no toilet, approx coords).

- FL **local** stage — DONE + committed: adds `3525302` (ids 4813–4858, 46 entries: county/city/regional + WMD), waterfront-audited in 6 sequential batch commits `a7a6343`→`5069fe6`. 19 on-water/view (10 lakefront, 2 riverfront, 1 bayfront, 4 lakeview, 2 riverview), 27 not waterfront. All deferred-to-local items folded in (Lake Stone, Newport, Otter Springs, Kelly Park/Rock Springs, Bill Frederick, Cotton Lake/NWFWMD, Pahokee/City, Istokpoga/SFWMD). Excluded: DuPuis Gate 3 (soft-sand access); Clay County Fairgrounds reclassified → private candidate (nonprofit fair assoc, not county gov). The audit ran one-agent-at-a-time (session-limit risk) with apply+commit after each batch; two batch-1 agents died on transient API 529s before a third succeeded — no data lost because nothing was applied until an agent returned clean.

**FL is essentially COMPLETE** (state, federal, private, local — all added + waterfront-audited). As of 2026-06-18 all 238 FL campgrounds carry `waterfront_evidence` (or `--AWH`); 0 unaudited.
- FL **legacy waterfront audit — DONE** (commits `cd29729`/`16dc0de`/`31dbba2`, ids 148–381, 23 entries, one-agent-at-a-time): all 23 confirmed `not waterfront` (spring/prairie/forest loops set back from the water they're named for; Ocala NF spring campgrounds have no rec.gov shoreline designation). No upgrades.
- FL **only remaining item — one private candidate**: **Clay County Fairgrounds RV Park** (run by nonprofit Clay County Fair Association → private, not local; NOT yet in DB). Vet under the private gate — chiefly confirm it's a *year-round transient* park, not a fairgrounds that only allows camping during events — then add + waterfront-audit if it clears. (If it doesn't clear, FL is fully done.)
- FL **state deferred items already DONE** (added in the state sweep — confirmed 2026-06-18): Karick Lake South = id 4719; Tate's Hell State Forest = Cash Creek 4722 + County Line OHV 4723.

**Process:** standing rule is [[feedback_sequential_sweep_agents]] (one agent at a time). The parallel-batch usage in this sweep was a TEMPORARY per-stage exception the user granted explicitly for state, then federal, then private — NOT standing. Default back to sequential unless the user grants it again for a specific stage.
**Dedup caveat:** dedup against existing must be **FL-scoped + coordinate-based**, not bare-name — a NY "Lake Eaton Campground" falsely blocked the FL Ocala one. Next id was 4744 at handoff.
