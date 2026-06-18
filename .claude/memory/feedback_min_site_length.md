---
name: feedback-min-site-length
description: "Don't add campgrounds whose largest drive-in sites cap at ~20 ft (EKKO is 23 ft)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c8ea6a71-08f2-45a1-8ff8-4a363d1ac421
---

EKKO is a 23-ft RV. Don't add a campground when its largest drive-in sites top out around 20 ft (or otherwise can't take a 23-ft rig), even though EKKO can occasionally squeeze into a 20-ft spot. Treat that as a disqualifier unless it's a genuinely special case worth flagging.

**Why:** the family would rather not rely on barely-fitting. Confirmed when excluding the C&O Canal NPS campgrounds — McCoys Ferry and Spring Gap both cap drive-in sites at ~20 ft, so both were left out despite Spring Gap being a requested bonus find.

**How to apply:** during the campground-data-curation site-size check, read the per-site max length (recreation.gov / NPS site pages); if no site fits a 23-ft rig, exclude. Relates to the [[reference-rvlife-price]] / Good Sam workflow and the general inclusion criteria in CLAUDE.md.
