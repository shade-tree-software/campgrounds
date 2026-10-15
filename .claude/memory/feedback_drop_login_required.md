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

**Softened by AWH 2026-10-14 (#3): "keep if website (not facebook) publishes prices and provides phone number."** So when only the booking calendar needs a login, the park stays if its own site posts the rates and a phone. Nine were kept on it: Edmond OK 6829 and 6834, Hells Canyon 9615, Linn County OR 11014, 11033, 11083 and 11084, Cresap Bay 10515, Crook County 11073. Jetty Park 13374 and Red Rock 13594 were dropped before #3; re-check them under it (Red Rock's city page posted no rate; Port Canaveral's Jetty Park page needs the driver browser to render).

Related: [[project_price_research]], [[feedback_require_live_web_presence]].
