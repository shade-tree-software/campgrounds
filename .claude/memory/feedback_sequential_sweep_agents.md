---
name: feedback_sequential_sweep_agents
description: "Run state-sweep / waterfront-audit subagents one at a time (sequential), never in parallel batches; keep each batch tiny (1 candidate) so there are frequent pause points"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9c3ecf0d-e001-42b3-a4d9-3445be29beb8
---

From now on, run campground state-sweep and waterfront-audit subagents **sequentially — one agent at a time**, not in parallel waves/batches.

**Why:** Parallel batches hit session limits, which causes all in-flight parallel agents to suddenly fail and lose all work in flight. Running a single agent at a time means far less collateral damage if a session limit is hit.

**How to apply:** Even though the audit pipeline docs describe "batches of ~8, waves of ~5", override that — launch one subagent, wait for it to finish and persist its results, then launch the next. Slower but more total work completed due to fewer catastrophic failures. Applies to detection sweeps and [[feedback_waterfront_evidence_in_json]] waterfront audits alike.

**Keep each batch TINY as well as sequential — ONE candidate per agent** (AWH
2026-09-15, mid-WV-sweep). First on a 7-candidate batch: "The batch is running too
long with no opportunity to pause if we start getting too close to the session
limit." Then, when that one batch had eaten half the session and still not
returned, ~3 was judged too coarse too: "dial back to 1 candidate for future, see
how it goes, and we can ramp back up if appropriate."

Sequential fixes the collateral damage from parallel failure; small fixes the
*other* half of the same problem. One agent researching 7 campgrounds runs long
enough that there is no safe moment to stop, and if the limit lands mid-run the
whole batch's work is lost anyway — sequential-but-huge reproduces the failure it
was meant to prevent. A ~3-candidate batch returns often enough to be a real
checkpoint: results land on disk, and the run can be stopped between batches
without losing anything.

More batches is the cost and it is the right trade — the same reasoning as the
parent rule, one level down.

**The measurement that settled it:** one agent researching 7 WV campgrounds consumed
**half a session** without returning. A batch is all-or-nothing, so that is half a
session of work that a limit landing one minute later would have destroyed.

**One candidate per agent costs more in total and that is accepted.** The fixed
overhead — reading the ~160-line instructions file, loading WebFetch/WebSearch — is
paid once per batch, so six 1-candidate batches burn more than two 3-candidate ones.
The trade is deliberate: granularity is the point, total throughput is not. Ramp back
up only if AWH says so.

**Write each agent's JSON to disk the moment it returns**, before launching the next.
The checkpoint only exists if the results are persisted; results left in the
conversation are lost with the session exactly like in-flight work.

