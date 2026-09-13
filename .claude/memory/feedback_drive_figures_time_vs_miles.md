---
name: feedback_drive_figures_time_vs_miles
description: AWH prefers a duration for a short drive and a mileage for a long one — the figure is only worth printing when the distance was the day's achievement
metadata:
  type: feedback
---

AWH, 2026-09-13: "I tend to prefer timespans (a one hour drive) for short
drives and mileage (500 miles) for long drives."

Confirmed by the 39 day-notes he wrote over generated drafts: **every mileage
figure of 131 miles or more survived the rewrite**, and 62, 66, 81, 89, 107,
122 and 123 were all cut or replaced by a duration — "South 66 miles to Casa
Vargas" became "An hour and a half south to Casa Vargas", "north 107 miles"
became "two hours out of Virginia", and "89 miles home" became "on to home".

**Why:** a figure earns its place when the distance was what the day
*achieved*. Under a couple of hours it wasn't, and "66 miles" is a number a
reader feels nothing about; the time is what they can picture. It is the same
test that keeps mileage off a round-trip day entirely
([[project_travelogue_capture_gap]]).

**How to apply:** under ~130 miles use the driving time in words, or no figure
at all; from ~300 up print the mileage; in between use whichever the day was
about. Never both for one leg, and never a derived pace or average. In
`process_rollups.py` this is a numbered rule in `SYSTEM`, and `driving_time`
was already in the dossier — the drafter simply had never been told when to
prefer it. Relates to [[feedback_summaries_say_less]].
