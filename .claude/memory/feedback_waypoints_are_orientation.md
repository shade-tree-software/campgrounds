---
name: feedback_waypoints_are_orientation
description: "Minor waypoints (gas stops, rest areas) are navigational landmarks for AWH — don't hide them to reduce clutter"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 81727cea-100e-42b3-9840-f0096b68cbc2
  modified: 2026-09-10T19:50:02.422Z
---

AWH, 2026-09-10, on the folded-waypoint chips: "I know that people don't care
about gas stations, but I use those stops to mentally orient myself about the
trip, and I don't like them being collapsed." Folding was disabled
(`WAYPOINT_FOLDING_ENABLED = False`) rather than deleted.

**Why:** the folding premise — nobody reads a trip for the gas station — is
true about what is INTERESTING and false about what the timeline is FOR. A fuel
stop outside a town you remember is a landmark in the day's sequence even when
it carries nothing to read. Measuring "663 of 747 waypoints carry nothing a
reader wants" answered the wrong question: nobody was struggling with the extra
rows, and the scaffolding they provide is what a reader navigates by.

**How to apply:** don't propose hiding, folding or summarising low-content
timeline items to reduce clutter — density is not the problem being solved. A
better answer is a lighter *rendering* (a compact one-line row rather than a
full card) that keeps every stop visible and in place. The same caution applies
to the rollup dossier's `unremarkable_stops`, which collapses the same items for
the same reason — it survives only because a written paragraph genuinely cannot
name forty stops, not because the stops are worthless. See
[[project_travelogue_capture_gap]].
