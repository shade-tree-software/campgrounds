---
name: feedback_sequential_sweep_agents
description: "Run state-sweep / waterfront-audit subagents one at a time (sequential), never in parallel batches"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9c3ecf0d-e001-42b3-a4d9-3445be29beb8
---

From now on, run campground state-sweep and waterfront-audit subagents **sequentially — one agent at a time**, not in parallel waves/batches.

**Why:** Parallel batches hit session limits, which causes all in-flight parallel agents to suddenly fail and lose all work in flight. Running a single agent at a time means far less collateral damage if a session limit is hit.

**How to apply:** Even though the audit pipeline docs describe "batches of ~8, waves of ~5", override that — launch one subagent, wait for it to finish and persist its results, then launch the next. Slower but more total work completed due to fewer catastrophic failures. Applies to detection sweeps and [[feedback_waterfront_evidence_in_json]] waterfront audits alike.
