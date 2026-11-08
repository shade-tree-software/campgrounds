---
name: project-season-and-notes-round2
description: 2026-11-08 season pass (151 rec.gov-calendar seasons vs agency) and notes round 2 (cut note text the group notes repeat) both COMPLETE; open items logged
metadata:
  node_type: memory
  type: project
  originSessionId: 63033443-99f7-4b5a-af4e-d10daf222e24
  modified: 2026-11-08T21:37:15.828Z
---

Both passes finished 2026-11-08 and are committed to master. Nothing has been pushed or deployed.

- **Season pass:** all 151 seasons derived from the recreation.gov calendar were re-read against the agency's own page; chunks are in `audit/season_calendar/out/`.
  - Usual finding: the calendar edge is where reservations stop. The open season is wider and first-come outside it.
  - Group-site-only rec.gov facilities give the group sites' dates, not the campground's (13291 and 13292 Onion Creek).
  - Open items are in `audit/season_calendar/followups.md`: first-come sites missing from `booking`, RV-length conflicts, two self-contradicting pages.
- **Notes round 2:** cut what the season, booking, fees and sites notes already say; those notes now show in the popup behind a "Show notes" link (chip rows fit one line on a desktop and two on a phone, with a clickable "+N more"; approximate seasons say "about" on the chip; AWH 2026-11-08). It covered 21 chunks; the questions it raised are in `audit/note_dupes/asks.md` and were not yet put to AWH.

Related: [[project-note-price-cleanup]], [[feedback-clean-up-notes]].
