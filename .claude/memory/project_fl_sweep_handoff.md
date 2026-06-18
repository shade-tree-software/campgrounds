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

**PENDING stages (FL) — verified 2026-06-18:**
- FL **waterfront audit of 23 legacy entries** (ids 148–381, empty `waterfront_evidence`, no `--AWH`): the LAST real FL task. Regenerate the list: FL + kind campground + no `waterfront_evidence` + no `--AWH`. Breakdown: 17 state (spring/prairie state parks — Wekiwa, Blue Spring, Rainbow Springs, Paynes Prairie, Oscar Scherer, Colt Creek, Alafia River, Lake Kissimmee, Highlands Hammock, Lake Griffin, Mike Roess, Kissimmee Prairie, Faver-Dykes — plus reclassified state forests Ross Prairie 156, Holder Mine 166, Tiger Bay 167, and Mutual Mine 170), 3 federal (Hopkins Prairie 148, Juniper Springs 282, Salt Springs 381), 2 hipcamp (Fresh Gardens 368, Gate to the Keys 369), 1 private (Shangrila 155). Mostly `not waterfront` but each owes the mandatory satellite look (a few spring/lake parks could earn view/on-water).
- FL **private — one reclassified candidate**: **Clay County Fairgrounds RV Park** (run by nonprofit Clay County Fair Association → private, not local; NOT yet in DB). Vet under the private gate — chiefly confirm it's a *year-round transient* park, not a fairgrounds that only allows camping during events — then add + waterfront-audit if it clears.
- FL **state deferred items are DONE** (were already added in the state sweep — confirmed 2026-06-18): Karick Lake South = id 4719; Tate's Hell State Forest = Cash Creek 4722 + County Line OHV 4723. No action needed.

**Process:** standing rule is [[feedback_sequential_sweep_agents]] (one agent at a time). The parallel-batch usage in this sweep was a TEMPORARY per-stage exception the user granted explicitly for state, then federal, then private — NOT standing. Default back to sequential unless the user grants it again for a specific stage.
**Dedup caveat:** dedup against existing must be **FL-scoped + coordinate-based**, not bare-name — a NY "Lake Eaton Campground" falsely blocked the FL Ocala one. Next id was 4744 at handoff.
