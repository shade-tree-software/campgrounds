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

Auth: `pa-ask-pass.sh` reads `PA_PW` from the gitignored `.env`, wired via
`SSH_ASKPASS` + `SSH_ASKPASS_REQUIRE=force` (OpenSSH 8.4+). Deliberately NOT `sshpass`
(needs a sudo install) — same askpass convention as [[the git PAT helper]]
`git-ask-pass-pat.sh`.

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

**This dev laptop has only ~4 GB free on `/`**, which is less than the ~7 GB photo set —
so sync photos to the SD card (`--dest`), not the repo. The preflight enforces this.

Related: [[project_usb_standalone_edition]].
