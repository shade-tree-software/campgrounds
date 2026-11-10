---
name: feedback_one_verifier
description: AWH 2026-11-10 — up to FOUR phase-7 agents at a time until further notice (was one since 2026-10-22)
metadata:
  type: feedback
---

**CURRENT (AWH 2026-11-10): "You may run four threads at a time until further notice"** — up to four background agents at once (verifiers and lead vetters count alike). Build each batch with queue.py before launching the next (un-applied batch files keep their ids out of later batches), apply results one at a time in the main thread, and keep the shared headless-browser flock. Revert to one when AWH says so.

History: AWH 2026-10-22: "Drop down to one thread only" — run a single phase-7 verifier agent at a time, launching the next batch only after the previous one is applied.

**Why:** AWH's call (no reason given); supersedes the earlier "TWO verifiers allowed" permission in [[project_phase7_verification]]. Same spirit as [[feedback_sequential_sweep_agents]] and [[feedback_limit_headless_browsers]].

**How to apply:** one background verifier; generate batch N+1 only after applying N. Don't go back to two unless AWH says so.

**Clarified (AWH 2026-10-22):** "one thread" is per session: each concurrent phase-7 session may run its own single verifier (e.g. the Montana cloud session beside the main run).
