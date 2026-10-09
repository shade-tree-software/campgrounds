---
name: feedback_15_amp_is_legitimate
description: 15A (and 20A) are rare but real campground pedestal amperages; hookups.electric allows 0/15/20/30/50
metadata:
  type: feedback
---

AWH 2026-10-09: "15A and 20A are rare but legitimate amperage values for campground pedestals."

The schema had pinned `hookups.electric` to 0/20/30/50, so every note saying "15-amp electric" was
stored with no amperage at all — the note-scan prompt and `recgov_hookups.snap_amps` both
dropped it as unrepresentable. Now `INT(0, 15, 20, 30, 50)` in `campground_schema.py`, the
`SYSTEM` prompt in `extract_fields.py`, `snap_amps` and docs/campground-schema.md all carry 15.

**Why:** a 15A-only site is a real fact a rig owner needs (it won't run an air conditioner), and
"unknown" hides it. Snapping still goes DOWN, never up, and anything under 15 is still omitted.

**How to apply:** "15A or 30A sites" -> 30 (highest at a site); "15-amp only" / "15 amp service"
-> 15; 15A loop alongside full-hookup sites of unstated amps -> omit (the highest is unknown).
The map's Electric filter treats 15 as electric (`amps > 0`). Backfilled 18 entries on 2026-10-09
(plus 14475 -> 30); 6666's rec.gov-catalog 50 was left despite its note saying 15A
([[feedback_trust_recgov_over_sweep_notes]]). `recgov_hookups.py` may now derive 15 for some
facilities it previously skipped — re-run its dry run where the RIDB cache lives before `--apply`.
