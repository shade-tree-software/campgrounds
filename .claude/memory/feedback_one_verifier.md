---
name: feedback_one_verifier
description: AWH 2026-10-22 — phase 7 runs ONE verifier at a time again (was two)
metadata:
  type: feedback
---

AWH 2026-10-22: "Drop down to one thread only" — run a single phase-7 verifier agent at a time, launching the next batch only after the previous one is applied.

**Why:** AWH's call (no reason given); supersedes the earlier "TWO verifiers allowed" permission in [[project_phase7_verification]]. Same spirit as [[feedback_sequential_sweep_agents]] and [[feedback_limit_headless_browsers]].

**How to apply:** one background verifier; generate batch N+1 only after applying N. Don't go back to two unless AWH says so.
