---
name: feedback-unread-retry-routes
description: AWH 2026-11-20 — for the 82 phase-7 entries left UNREAD behind bot walls, headless browser / Wayback / strong secondary sources are allowed (scoped exception)
metadata:
  type: feedback
---
AWH 2026-11-20: for the phase-7 entries left UNREAD because their own sites refuse bots (IL 14, WI 26, VT 1, MN 9, ND 31, AB 1), I may retry via archive/cache copies, proxies, a disguised UA, a headless browser or Claude in Chrome (my pick), and a strong secondary source may stand in for the operator's own page.

**Why:** the bot walls left ~82 entries with no phase-7 read at all; the no-retry rule ([[feedback-limit-headless-browsers]] context, the agent template's rule 13) was the blocker.

**How to apply:** SCOPED to those unread entries, not new batches — new state batches (SD on) keep the no-retry rule. Chosen order (kit/unread/retry_rule.txt): headless Chromium with a normal UA at human pace → dated Wayback capture (pre-2025 = stale for rates/season/status) → strong secondary (operator's own booking engine, same government's documents elsewhere, state tourism/association listing). No proxies, never solve a captcha, never log in. Aggregators stay corroboration only. Batches u-01.. via audit/verify/kit/unread/build.sh; status in audit/verify/kit/unread/RESUME_UNREAD.md.
