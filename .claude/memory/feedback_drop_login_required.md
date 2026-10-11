---
name: feedback-drop-login-required
description: AWH 2026-10-11 - drop a campground whose rates or availability can't be seen without an account or login; a login required only at checkout (rec.gov, ReserveAmerica) is fine (AWH confirmed)
metadata:
  type: feedback
---

AWH 2026-10-11, after hearing that Jetty Park's rates needed a CampLife login: "drop anything that requires an account or login."

Applied the same day to the two unpriced entries whose rates and booking sat behind a login:
- Jetty Park 13374 (Port Canaveral FL): CampLife said "Login required ... for all sites except pavilions".
- Red Rock Park 13594 (Gallup NM): its bookmysites links open a login page.

Both are logged in `audit/price_research/dropped_2026-10-11.jsonl`.

**Why:** a campground you can't even price without signing up isn't one AWH will plan around. It also matches his standing refusal to have me create accounts or log in to booking sites, so these entries could never be priced from here.

**How to apply:**
- In price research and sweeps, if the rates or availability can't be seen without a login or account, drop the entry (or don't add it) and log the why. Don't ask AWH to log in for it.
- **Scope, confirmed by AWH 2026-10-11:** "A login is fine for checkout but not if it's required to see rates/availability." So recreation.gov, ReserveAmerica and similar engines, which show rates and availability publicly and want an account only to complete a booking, stay.
- A captcha (ResNexus, Firefly, Bonfire, Itinio) or a cart-only fee is not a login. Those still get the saved-page route ([[feedback-missing-rate-is-unresearched]]).

Related: [[project_price_research]], [[feedback_require_live_web_presence]].
