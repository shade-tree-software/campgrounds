---
name: app-is-private-family-only
description: "EKKO Trips is a private family app — all accounts/share links go to family & friends; family home locations SHOULD be visible to all users, never treat as a privacy leak"
metadata: 
  node_type: memory
  type: project
  originSessionId: e29cc85c-749a-4093-92ca-f238308f5729
  modified: 2026-07-26T11:41:06.907Z
---

EKKO Trips is **not a public app**. Share links and non-admin accounts are given only to family members and friends (stated by AWH, 2026-07-26).

**Why:** UX/security reviews naturally flag "family home coordinates shipped to read-only viewers" as a privacy leak. For this app that's wrong — every viewer is family or a trusted friend, and seeing family home locations (red house markers, `family_locations` in `TRIP_BOOT`) is a *feature*, not a leak.

**How to apply:** Never propose hiding family/home locations, family markers, or family labels from non-admin or share-link users. Payload-size arguments for trimming data are still fair game; privacy arguments are not. (The repo itself is public, which is why the home *street address* stays in gitignored `home.json` — that rule is unchanged; this is only about what logged-in viewers of the running app can see.) See [[ux-review-2026-07]].
