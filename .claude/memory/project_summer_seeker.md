---
name: project-summer-seeker
description: "index.html belongs to a separate \"Summer Seeker\" app sharing this repo with EKKO Trips"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6f766309-cc83-4ca8-9f3e-1c93119374dd
---

`templates/index.html` is part of "Summer Seeker," a separate app that shares the same repo and some data (e.g. `campgrounds.json`) with EKKO Trips but is otherwise independent. It is intentionally standalone — does not extend `base.html`, does not share nav. Routes like `/search` and `/geocode` (used by index.html) belong to Summer Seeker, not EKKO Trips.

**Why:** Two apps cohabit one Flask process today; the user has flagged that separating them more cleanly is a possible future cleanup but is not a current priority.

**How to apply:** When a task says "the app" or scopes mobile/UI/feature work, default to EKKO Trips (everything except `index.html` and its `/search` + `/geocode` routes). Don't bundle Summer Seeker fixes into EKKO Trips work unless the user asks. If asked to "separate the two apps," that's a structural refactor — propose a plan before acting.
