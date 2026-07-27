---
name: reference_sync_from_pa
description: ./sync-from-pa.sh pulls trip data + photos incrementally from PythonAnywhere over rsync; use it instead of backup/restore tarballs for routine refreshes
metadata: 
  node_type: memory
  type: reference
  originSessionId: d8015b25-3a69-4c9c-b79b-cd3a86bc1083
  modified: 2026-07-19T14:42:35.715Z
---

`./sync-from-pa.sh` (repo root, added 2026-07-19, commit `3bc74f1`) incrementally pulls
`trip_data/` and `static/uploads/` from the live PythonAnywhere app over rsync+ssh.
Use it for routine refreshes; `backup.sh`/`restore.sh` tarballs are for seeding a new
machine, and move the whole ~7 GB dataset every time.

```
./sync-from-pa.sh                              # data + photos into this repo
./sync-from-pa.sh --data -n                    # trip_data only, dry run
./sync-from-pa.sh --dest /media/andrew/EKKO/app   # refresh the USB/SD card
./sync-from-pa.sh --delete                     # opt-in exact mirror
```

Auth (changed 2026-07-27): a dedicated key `~/.ssh/pa_sync_ed25519`, pinned on PA to
`command="/usr/bin/rrsync -ro /home/shadetreesoftware/campgrounds",restrict` — read-only,
no shell. **rsync paths are therefore relative to that root** (`$PA_HOST:/trip_data/`,
no `/home/...` prefix). The old `PA_PW`-in-`.env` + `pa-ask-pass.sh` askpass path is GONE
(script deleted, var removed); no account password is stored on this machine. See
[[reference_pa_ssh_keys]].

**Gotchas baked into the script — don't undo these:**
- **`--no-human-readable` in the space preflight is load-bearing.** With rsync's `-h`
  the stats line reads `Total transferred file size: 4.45G bytes`; stripping non-digits
  yields `445`, an underestimate that silently defeats the free-space check. That bug
  started a 7 GB pull onto a 4 GB root filesystem before it was caught at 94% full.
- **`-rlt` (not `-a`)**: preserving mtimes is REQUIRED because the app's thumbnail cache
  and track cache are mtime-keyed — clobbering timestamps silently invalidates them.
  `-a`'s `-o/-g` need root and only add noise.
- **Always excludes `secret_key` + `dev_cert.*`** — pulling PA's session secret would
  invalidate local logins and spread a production secret. Also skips `.thumbs/`
  (regenerated on demand, large) and `.trash/`.
- **No `--delete` by default**, so a local-only file is never silently removed.

**Bug fixed 2026-07-20 (preflight must NOT decide "up to date"):** the space preflight
prices only file TRANSFERS (bytes to send), not DELETIONS, and returns empty on a
transient preflight-rsync hiccup. It used to `echo "already up to date"; return 0` in
that case — silently skipping the real rsync, so pending `--delete` removals never
applied (observed: a `--delete` run reported "up to date" while a dry-run clearly listed
34 deletions). Now the preflight only gates on disk space and always falls through to the
real rsync. **Also: never run sync-from-pa from a dir where `static/uploads` is a SYMLINK
(e.g. the `~/ekko-sdcard-test/app` test rig) — rsync won't sync into a symlinked dest dir,
so the pull no-ops. Run it from the real working repo (`~/Dev/campgrounds`).** Both bit a
trip-92 photo-scramble repair: the local copy was stale (PA was correct), and neither the
symlinked test-rig run nor the buggy-preflight run actually pulled the fix.

**This dev laptop has only ~4 GB free on `/`**, which is less than the ~7 GB photo set —
so sync photos to the SD card (`--dest`), not the repo. The preflight enforces this.

Related: [[project_usb_standalone_edition]].
