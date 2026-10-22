# Phase 7 West Virginia helpers (batches p3-52..p3-61)

Copied 2026-10-21 from that session's scratchpad so a later session can use them; scratch directories don't outlive a session. These are one-off scripts written by verifiers: copy them, don't edit them in place. Several read cached data (e.g. `wvt.json` booking-site pulls, `trip_data/ridb_campsites.json`) that was not copied, so re-fetch it first.

- **book.wvstateparks.com:** `p3-52/` has the tile queries (and audit/state_park_fees/wv_tiles.py). `p3-55/dec.py` decodes each unit's attribute codes (544 pull-through, 545/546/547 30/50/20 amp, 553-557 RV-length classes, 736/737 riverview/riverfront, 738-740 full/water/sewer).
- **FareHarbor:** `p3-59/fh.py` reads calendars and availability ids.
- **Campspot:** `cs1.py` / `cs2.py`. **Browser:** `bw.py` (needs PYTHONPATH=~/.cache/ekko-pw; run under `flock /tmp/ekko-headless-browser.lock`).

The verifier brief used for these batches is `../prompt_template_wv.txt` (p3-61's). For a new batch, swap the paragraph that starts "All twelve are WEST VIRGINIA entries" and the batch ids, point its helper and scratch paths at the new session's directories, and launch the verifier with "read your brief from <file>".
