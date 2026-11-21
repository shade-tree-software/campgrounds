---
name: feedback-unread-retry-routes
description: AWH 2026-11-21 — ALL verifiers may fall back to a headless browser, then an internet archive, when a site blocks plain automated requests (was scoped to the unread-retry pass 2026-11-20)
metadata:
  type: feedback
---
AWH 2026-11-21: "All future verifiers may fall back to using a headless-browser when blocked on plain automated requests. They may also try internet archives." This lifts the 2026-11-20 scoping, which allowed these routes only for the ~82 UNREAD entries (kit/unread/).

**Why:** Castlewood 5864 (SD, p3-560) went unread on a Cloudflare 403 to curl, yet one headless-Chrome load read the city's page with the rate, sites, hookups and booking phone. The no-retry rule was costing entries that were easy to read.

**How to apply:** the rule text lives in audit/verify/kit/sd/agent_prompt_template.txt (copy it into any new state's kit): (1) headless Chromium with a normal UA at human pace, one browser at a time under the flock ([[feedback_limit_headless_browsers]]); (2) a dated Wayback capture (pre-2025 = stale for rates/season/status). Still no captcha solving, no proxies/VPN/reader services, no logins. "Strong secondary source standing in for the operator" was allowed only in the unread pass; AWH didn't extend it, so aggregators stay corroboration only.
