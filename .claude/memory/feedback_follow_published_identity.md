---
name: feedback_follow_published_identity
description: "AWH 2026-10-14 (#6, #8): an entry's phone, name, ownership and links follow what the park publishes now - switch to its published number, rename to its current name, fix ownership from what is actively published, remove dead or unclaimed Hipcamp/RoverPass links; no need to ask"
metadata:
  type: feedback
---

AWH's answers of 2026-10-14 to the RoverPass/CampLife report:
- **#6 phone:** "prefer a published phone number to our own that cannot be confirmed on any website." Applied as: the number the park publishes (its own site first, then its booking listing) replaces ours whenever they differ. 7 switched in 768c56d, 38 in the RoverPass operator pass (37768ea).
- **#8 name:** "rename our name to currently-published name" (new owner, rebrand: Joseph Stewart County Park 10641; 10 renamed in 37768ea).
- **#8 ownership:** "If our ownership looks wrong, change it to what is actively published." Check first, then set it (Black River 5088 hipcamp -> private; Campus RV Park 1981 local -> private).
- **#8 links:** "Remove dead or unclaimed hipcamp links" (Seidels 2230, Bert's 2231: 'Coming soon', takes no bookings). #8f extended it to RoverPass: remove an unclaimed RoverPass link whenever the entry is touched (143 removed in 37768ea). A town or county park with no page of its own keeps its link (2026-10-01).

**Why:** the entry is for planning a stay; a stale phone, an old name or a dead link costs a call or a search just when the family needs the park.

**How to apply:** whenever an entry is touched for any reason, check these four against the park's own pages and fix them in the same edit. AWH (#8f): "Make changes subject to our existing rules and precedents, no need to propose or confirm with me on these." docs/campground-curation.md states the rules. Related: [[feedback_require_live_web_presence]], [[reference_roverpass_api]], [[feedback_clean_up_notes]].
