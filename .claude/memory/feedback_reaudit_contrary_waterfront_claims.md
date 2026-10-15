---
name: feedback_reaudit_contrary_waterfront_claims
description: "AWH 2026-10-14 (#7): re-audit waterfront whenever an operator or booking engine claims water differently from our call, in either direction; the claim is a lead, never the verdict; sources that settle it (operator My Maps KML, aerial photos, Campspot site map, schema.org/RoverPass coordinates, NC911 Wayback orthos)"
metadata:
  type: feedback
---

AWH 2026-10-14 (#7): "re-audit any that claim waterfront when the claim differs from ours." Done for 11 (3409ab6 plus Woods-N-Waters 14481, which that commit missed and was re-audited later the same day: the "Waterfront Site" tag sat on whole site types in the inner loops, so it stayed `not waterfront`) and for 3 in the RoverPass operator pass (Holly Park 7574 and Scenic View 7777 lakefront, K-Park 14429 creekside; pins moved for Crazy Horse 4476, Stony Fork 4295 and Angel Nest 8133).

**Why:** booking engines name site types after the water ("Waterfront Site", "Lakeside", "Canal Spaces"). When ours disagrees, one of the two is wrong, and the evidence gate decides which.

**How to apply:** treat the claim as a lead in both directions and run the normal gate (satellite look plus per-site evidence). A tag on a whole site type proves nothing about any one site; map the sites. Sources that settled them:
- the operator's Google My Maps, exported as `https://www.google.com/maps/d/kml?mid=<id>&forcekml=1` (per-site points);
- the operator's own aerial photos (home-page galleries);
- Campspot's per-site map: `audit/private_gap_browser/campspot_map.py` colours chosen types on the park's own SVG;
- the coordinates in a page's schema.org `geo` block or a RoverPass record, to check our pin while you're there: the 2026-10-14 re-audits moved five (4320 ~140 m onto its loop, Wild Nature 12961 ~500 m off its entrance road, Angel Nest 8133 900 m, Crazy Horse 4476, Stony Fork 4295). An engine's own pin can be wrong too: Campspot's for 4320 is 1.3 km off, in residential woods;
- in North Carolina, Esri Wayback's NC911 releases (0.15 m, leaf-off; release 20512 decided Stony Fork 4295, 22252 decided 4320).
Records: audit/price_research/waterfront_reaudit_2026-10-14/, audit/price_research/roverpass_ops_2026-10-14/waterfront_reaudit.py. Related: [[feedback_waterfront_evidence_in_json]], [[feedback_verify_image_reads]].
