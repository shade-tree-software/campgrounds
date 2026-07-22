---
name: project_dvd_transfer_z15
description: Work machine is DVD-only (no USB/SD allowed off it) — street-us-z15.pmtiles is split into 3 dual-layer DVD parts in /data/ekko-us-build/dvd-split/
metadata: 
  node_type: memory
  type: project
  originSessionId: d73f68ff-c0cc-41c8-8f13-f881a2c4f99c
  modified: 2026-07-22T12:31:26.829Z
---

The work machine has a **no-USB-stick / no-SD-card policy — burning to DVD is the only way to get files off it**. Any large artifact built there (tile files, archives) must be split to disc-sized parts, not copied to removable flash. The earlier corridor-era tile files were moved off this way too.

As of 2026-07-22, `/data/ekko-us-build/street-us-z15.pmtiles` (19,964,936,219 B, sha256 `3f44dc17597fc95b5553dd4785fc6da220315f4184ab24ed3bd9a80473661f38`) is staged for transfer in **`/data/ekko-us-build/dvd-split/`**:

- 3 parts of ~6.655 GB (`street-us-z15.pmtiles.part0..2`) — one per **dual-layer** DVD+R DL (8.55 GB), burn as UDF at low speed. An earlier 5-part single-layer split (4.4 GB parts) was replaced at the owner's request.
- `MANIFEST.sha256` — per-part + whole-file hashes.
- `assemble-from-discs.sh` — **the one to use**: appends each disc straight into the output as it's inserted, so the destination needs only the ~18.6 GiB of the finished file, never the parts too. Reads each disc once (`cat | tee -a | sha256sum`), rolls back on a hash mismatch, and resumes after an interruption from the output's byte offset. Tested end-to-end on the real data (full run, resume, and bad-disc rollback).
- `reassemble.sh` — plain concat, only if ~40 GB free.
- `README-DVD.txt` — burn + assembly instructions incl. Windows equivalents.

**Destination:** `<card>/app/tiles/street.pmtiles` (the app's expected filename — NOT `street-us-z15.pmtiles`; it auto-detects z0–15 from the header). The card is ext4, so no FAT32 4 GiB cap. Assemble to `street.pmtiles.incoming` then `mv`, delete the old street file first (64 GB card can't hold both), and answer `y` to the final verify since it re-reads off the card. See [[project_usb_standalone_edition]] for the card layout and the flash-reliability history.

Delete `dvd-split/` (another 18.6 GB) once the discs are burned and verified.
