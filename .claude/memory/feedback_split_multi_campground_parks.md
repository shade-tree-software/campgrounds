---
name: feedback-split-multi-campground-parks
description: Split a one-pin park entry into its campgrounds only when phase 7 runs into it, and only for campgrounds at separate places (own entrance, ~1 km+ apart)
metadata:
  type: feedback
---
A park entry with one pin that covers several campgrounds gets split into one entry per campground (AWH 2026-10-22), under two limits:
- **Only campgrounds at separate places**: their own entrance or road, roughly 1 km+ apart (Falls Lake 258: Rolling View vs Holly Point, 3-4 km). Adjacent named loops of one campground area (Ludington's Pines/Cedar/Beechwood) stay one entry.
- **Only when phase 7 runs into one that clearly needs it.** Don't go looking for split candidates on their own (AWH declined a DB-wide sweep; a text scan found ~100-125 park entries naming 2+ campgrounds).

**Why:** the harm is a pin on the wrong part of a lake, which a park-level entry produces; splitting adjacent loops adds entries with no map value.

**How to apply:** verifier briefs ask the verifier to flag such a park with each campground's name, coordinates, site count and booking link. Each new campground then needs the full curation pipeline (pin, waterfront gate on imagery, inclusion evidence, fields); the original id stays on one of them, and an --AWH note is not copied onto a campground it may not describe. Related: [[project-phase7-verification]].
