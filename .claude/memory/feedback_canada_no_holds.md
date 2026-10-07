---
name: feedback-canada-no-holds
description: Canada private gap (AWH 2026-10-07) - never hold for AWH except a permanent human-only bot blocker; blank/non-loading sites are skips; rate-limit blocks mean back off and retry
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5379d1c7-868c-4493-9893-a20ec48dbbb4
  modified: 2026-10-07T23:49:25.426Z
---

For the Canada private gap, do not hold campgrounds for AWH to look at. The one exception is a PERMANENT bot blocker that only a human can pass (an "I am human" interstitial or CAPTCHA that shows up on the first visit).

- A site that won't load or loads blank is a **skip** ("no readable web presence"), not a hold.
- A blocker that appears only because we hit too hard (ResNexus after a few dozen parks, 429s) means **back off, wait, and retry later in the session**. It is not a hold and not a skip.

**Why:** in the US pass, holds piled up and AWH worked them by hand on another machine. That isn't wanted for Canada.

**How to apply:** each verdict is add/skip, except the rare permanent-captcha hold. Record the skip reason as which kind of no it was (blank site vs closed vs price). Related: [[project-private-gap]], [[feedback-limit-headless-browsers]].
