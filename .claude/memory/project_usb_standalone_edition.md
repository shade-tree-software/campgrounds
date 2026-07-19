---
name: project_usb_standalone_edition
description: "A standalone offline USB-stick edition of the EKKO Trips app; layout, build recipe, and the offline tile pipeline (satellite DONE 2026-07-19, street rendering) — see STATUS + RESUME sections"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8d60efa1-9fa1-4ef7-b075-4178d82597ae
  modified: 2026-07-19T14:22:27.881Z
---

Built a fully self-contained, offline-capable USB edition of the EKKO Trips app on 2026-07-17 (owner's request). Runs on any x86_64 recent Linux Mint with NO system Python and NO internet.

**>>> STATUS 2026-07-19 (end of session): CARD IS DONE & WORKING except street.pmtiles,
which is to be built on a BIGGER MACHINE and dropped in. See
`usb/BUILD-STREET-ON-BIG-MACHINE.md` (committed + pushed, `f2542ad`).**

**The ONLY remaining step:** on a >=16 GB RAM machine, clone the repo, restore `trip_data/`
+ `home.json` (via `./backup.sh` tarball — the corridor is computed from the real GPS
tracks, which are gitignored), bump `JAVA_HEAP=8g` / `RENDER_THREADS=8` in
`usb/build-street.sh`, run it with `--poly-zoom 11`, then copy the single output file to
`<card>/app/tiles/street.pmtiles`. No code change, no restart flag — the app detects the
file at request time.

**Why it moved off this laptop:** the render needs ~10 h here (3 GB RAM). Measured
`osm_pass2` at ~800 ways/s of ~29.8M ways with heap pinned at 1.5-1.6G/1.8G. Tuning
attempts (z12 corridor, 2 threads, sparsearray nodemap) only got 15 h -> 10 h. NOTE the
two hypotheses that were TESTED AND DISPROVED, so nobody retries them: (1) tightening the
corridor z11->z12 cut only 16% of data, not the ~3x predicted (the trips run through dense
metro areas, so buffer width barely matters); (2) dropping `--complete-ways --complex-ways`
saves only 4% of nodes. The box is simply undersized; on 16 GB it is <1 h.

**Card state (verified end-to-end from the card's OWN python 3.12.11):** app at `f2542ad`,
clean tree; `/login` 200, `/` 302, `/sw.js` 200; satellite tile served byte-identical
(md5 match, `200 image/jpeg`); `/tiles/street.pmtiles` 404 -> satellite fallback active;
all vendored assets (tile-layers, protomaps-leaflet, leaflet js/css/marker images) 200.
`START-EKKO.sh` exports `EKKO_LOCAL_TILES=1` when `app/tiles/` exists. Build scratch
(`.build`, 8.1 GB) deleted — card now 14 GB used, **42 GB free**.

**satellite.mbtiles converted OUT of WAL mode** (`journal_mode=delete`) so it is a single
self-contained file — a removable card left with `-wal`/`-shm` side files after an unclean
unmount plus a read-only open is fragile. Keep it that way.

**Graceful degradation added (`f2542ad`)** so "local tiles on, street store absent" is a
proper state, not a broken half-install: `_tile_config()` advertises a local street source
only when the file exists, and `ekkoStreetLayer()` returns NAIP imagery when there is none
(every caller does `.addTo(map)`, so returning nothing would leave a white map).

---

**>>> STATUS 2026-07-19 (mid-session): TILE PIPELINE — satellite DONE + verified.**

**2026-07-19 tile-pipeline session (commits `5e9c4d7`, `c16b6b8`):**
- **All app-side plumbing is DONE and verified.** The missing link was that
  `static/vendor/protomaps-leaflet.js` was vendored but no template loaded it — now loaded
  from `base.html` + `trips_poster.html` gated on `tile_config.mode == 'local'`, so online
  pages don't pay ~100 KB and PA is byte-for-byte unchanged. Verified: local mode emits the
  tag, `/tiles/street.pmtiles` answers Range requests (206 + correct Content-Range, PMTiles
  magic) as protomaps-leaflet requires; with the env var unset pages still emit CDN URLs.
- **SATELLITE COMPLETE:** `app/tiles/satellite.mbtiles`, **200,538 tiles / 5.0 GB** (z0-16,
  91,922 at z16; ~25 KB/tile, so a bit over the 4 GB estimate). Verified END-TO-END through
  the Flask route: byte-identical md5, `200 image/jpeg`, out-of-corridor tiles 404 cleanly.
- **STREET in progress:** corridor spans **21 states + DC** (point-in-polygon over the 103,184
  corridor points; PA/VA densest). Pipeline = `usb/build-street.sh`: emit corridor .poly ->
  download each Geofabrik extract -> osmconvert clip (raw deleted right after) -> hierarchical
  merge -> planetiler. Clips: 23 files / 2.3 GB. Merged `corridor.osm.pbf` = **2.28 GB**.
  Render running at `-Xmx1800m --threads=3`.
- **Corridor width = z11** (`--poly-zoom 11`, ~29 km each side), NOT the z10 used in the
  Delaware test — z10 was too much data for this box. `--poly-zoom 10` widens it if wanted.

**THREE tooling bugs found + fixed (all "succeeds loudly while doing the wrong thing"):**
1. **osmconvert defaults to uncompressed .osm XML regardless of the `-o=` extension** — must
   pass `--out-pbf`. Silently turned a 326 MB PA extract into a **6.3 GB** clip (exit 0, data
   correct, wrong container). 22 states of that would have exhausted the card. Only the
   implausible 20x size ratio gave it away.
2. **`--rate` was never the NAIP bottleneck** — serial fetching is bound by NAIP's ~0.3 s
   round-trip, so a 20 req/s cap delivered **3/s** (17 h ETA). Now fetches on a thread pool
   (`--workers`, default 8) => **19-20/s, 0 failures, ~2.6 h**. The rate cap is still a real
   ceiling, now a lock-guarded shared slot clock across workers.
3. **osmconvert refuses >1 `.pbf` input** ("more than one .pbf input file is not allowed") —
   it only merges `.o5m`/`.osm`. So convert clips to `.o5m`, merge, emit `.pbf`. Then merging
   all 23 at once got **OOM-killed** (NAIP running concurrently on a 3 GB box) => merge
   hierarchically in groups of 6, resumable per group.
- Planetiler also OOM'd at `-Xmx1400m` (300 MB in-heap sortedtable index + 4 threads of
  feature buffers; it mmaps ~3.5 GB of node locations and needs page cache left over).
  1800m + 3 threads cleared it.

**Machine constraints that drove all of the above (this box, not the card):** 3 GB RAM,
4 cores, only ~4 GB free on `/`. Hence: stage EVERYTHING (downloads, clips, planetiler
tmpdir) on the card, and treat MEMORY as the binding constraint whenever two jobs overlap.
NAIP (network-bound, ~0.4 MB/s of writes) is safe to overlap with a bulk card writer; two
bulk writers are not (that is what wedged the old counterfeit stick).

---

**>>> STATUS 2026-07-18: v1 REBUILT on a good 64 GB drive + Leaflet now bundled locally.**
The build tooling is saved durably in the repo at `usb/` (START-EKKO.sh, build-env.sh,
update.sh, restore-backup.sh, requirements-ekko.txt, README.txt) — copy those to a fresh
stick's root to rebuild.

**2026-07-18 progress:**
- New **64 GB USB drive** (`/dev/sdb1`, USB): speed-gated at **53.8 MB/s** + clean 500 MB
  readback checksum (the retired 57 GB stick was counterfeit: <1.7 MB/s, wedged the kernel).
  Reformatted ext4 label `EKKO`, chowned to uid 1000, mounted at `/media/andrew/EKKO`.
- **v1 rebuilt & verified** on it: `python/` (533 MB, relocatable CPython 3.12.11 + deps via
  `build-env.sh`) + `app/` (shallow master clone + seeded users/home/trips/92 track-cache;
  uploads empty). Smoke test from the card's own python: /login 200, / 302, /sw.js 200,
  serving exe = card python. Build discipline held: env build to card first, clone staged on
  local disk then copied — never two USB writers at once (what wedged the bad drive).
- **Leaflet bundled locally (committed f3a4d77, on master):** self-hosted Leaflet 1.9.4 at
  `static/vendor/leaflet/` (js/css/marker+layer images), all 5 map templates point at it via
  `static_v()`; each sets `L.Icon.Default.imagePath` explicitly because static_v's `?v=`
  suffix defeats Leaflet's auto icon-path regex (the map-picker default marker is the only
  non-divIcon marker). SW bumped v5->v6: precache the vendored assets + serve `/static/vendor/`
  cache-first with `ignoreSearch`. Removes the unpkg CDN runtime dep (helps prod too). Synced
  to the card app/. **This closes the "bundle Leaflet locally" TODO below.**
- STILL TODO: the offline **tile pipeline** (next). Design fleshed out in `usb/TILE-PIPELINE-DESIGN.md`.

**Stick layout (at stick root):**
- `python/` — relocatable CPython 3.12 from astral-sh/python-build-standalone (release tag `20250612`, `install_only` gnu build) with all app deps pip-installed into its own site-packages (~533 MB). Fully relocatable — no absolute paths baked in.
- `app/` — shallow git clone of the public repo (`master`) + seeded gitignored data (`users.json`, `home.json`, `trip_data/`). No `static/uploads` photos on the source dev machine, so uploads started empty.
- `START-EKKO.sh` — computes its own dir via `readlink -f`, sources `app/.env` if present, waits on the port via bash `/dev/tcp`, `xdg-open`s the browser, then runs `python ekko_trips_app.py --http --port 5001` (localhost is a secure context so `--http` is fine and dodges cert warnings).
- `restore-backup.sh` — puts portable python on PATH, delegates to the repo's own `app/restore.sh` (which validates JSON with `python3`).
- `update.sh` — `git pull --ff-only origin master` + `pip install -r requirements-ekko.txt` (needs internet + git on host; repo is public so no auth).
- `build-env.sh` — (re)downloads python-build-standalone + installs deps; `--fresh` re-downloads the interpreter. This is the reproducible builder.
- `requirements-ekko.txt` — the COMPLETE dep set (the in-repo `ekko_trips_requirements.txt` was missing geopy/geographiclib/requests/certifi/etc that the app actually imports).
- `README.txt`.

**Key decisions / gotchas:**
- Deliberately NO `.env` on the stick (owner chose this): a normal offline user needs none of `FLASK_SECRET_KEY` (app auto-persists one to `trip_data/secret_key`), `TIMELINE_*` (maps use cached `track_cache/`), `RIDB_API_KEY`, or `GITHUB_PAT` (public repo). Drop an `.env` into `app/` later to light up online admin extras.
- Stick is ext4; its root mounted root-owned — owner had to `sudo chown -R andrew:andrew <mnt>` in a REAL terminal first (`!`-prefix sudo can't read a password). Files owned by uid 1000 → writable by the primary user on a standard single-user Mint machine.
- Do NOT use a host `python -m venv` (not self-contained — references system stdlib). python-build-standalone is the correct portable approach.
- Verified end-to-end: launched via the real `START-EKKO.sh`, `/login` → 200, `/` → 302, serving process `exe` confirmed to be the stick's `python/bin/python3.12`.

**Build tooling now lives in-repo at `usb/`** (recreated 2026-07-17 after the scratchpad staging was wiped). To build a stick: format ext4, chown root to uid 1000, copy `usb/*` to the stick root, run `./build-env.sh` (needs internet), `git clone --depth 1 <repo> app`, seed `users.json`/`home.json`/`trip_data/` from the live repo. **Build on FAST local disk then copy, OR serialize USB writers — never run the pip build and the git clone to the same USB at once (they starve each other; that timed out).**

---

## RESUME HERE (picking this back up later)

**Where we stopped:** v1 built + verified on the original **15 GB** stick (works, app launches in ~2 s there). Then decided to move to a bigger stick to also carry **photos (~8 GB, growing) + offline map tiles**. Reformatted a 57.6 GB stick (ext4, label `EKKO`) and rebuilt onto it — but that stick is **DEFECTIVE** (USB 2.0 "General USB Flash Disk"): write speed <1.7 MB/s, `sync` stalls for minutes, one readback threw an `Input/output error`, and a 100 MB write wedged `dd` + the `jbd2` journal thread in uninterruptible `D` state (`rq_qos_wait`). Diagnosis: cheap/counterfeit/failing flash. **Retired it.** Owner is to get a genuine, fast, reputable-brand **USB 3.0 stick or small external SSD, ≥64 GB**.

**First thing on resume:** with the new drive plugged in, run a BOUNDED speed test BEFORE building — `timeout -s INT 30 dd if=/dev/zero of=<mnt>/bench.tmp bs=1M count=200 conv=fdatasync status=progress` (a good drive does 200 MB+flush in a couple seconds; the bad one never finished). Only build if it passes. Then chown + rebuild from `usb/`.

**Sizing (measured from the 92 cached GPS tracks: 102,032 pts, 55,653 km of route):** full tile pyramid z0–16 with a ±1 corridor buffer = ~198k tiles ≈ **~4 GB per basemap layer** (@~20 KB/tile); tight/no-buffer = ~51k ≈ ~1 GB. Owner chose **BOTH basemap layers** (street + satellite). Total budget ≈ 0.55 (base) + 8 (photos) + ~7.5 (both layers) ≈ **~16 GB**, so ≥64 GB drive with headroom.

**Tile pipeline — DESIGN AGREED, NOT YET BUILT:**
- Tiles are **stick-only, gitignored** → they must NEVER be committed / reach PythonAnywhere. PA keeps using live OSM/Esri. The only code that reaches PA is a small Flask `/tiles/<z>/<x>/<y>` route that is **inert unless a local tile store is present** (gate on a dir/env), so online behavior is unchanged.
- App switches tile source via a server-provided config/env (e.g. `EKKO_LOCAL_TILES=1` set by START-EKKO.sh) → templates render `/tiles/...` on the stick, normal CDN URLs online. Multiple map templates hardcode tile URLs today (`trip_detail`/map.js, `trips_map`, `campground_map`, `campground_manage`, `map-picker`) — needs one shared switch.
- **Sources (free + legal, no ToS violation, no accounts): street = self-render from free Geofabrik OSM extracts; satellite = USGS NAIP (public-domain US aerial). Do NOT bulk-scrape OSM public tiles or Esri** (both forbid it). Store as MBTiles or z/x/y on the stick.
- `fetch-tiles.sh` (future): reads current trips.json + campgrounds, computes per-area bboxes + zoom range, downloads only MISSING tiles (incremental). Fold into `update.sh` optionally. This is how NEW trips get tiles later.
- Also TODO: **bundle Leaflet's own JS/CSS/marker-images locally on the stick** (app loads Leaflet from unpkg CDN — `trip_detail.html:6-7` — and the service worker doesn't cache it, so a truly-fresh offline machine can't init the map). Small (~150 KB), needed regardless.

**Separate perf bug found (affects production too, not stick-specific):** trip GPS tracks render slowly (~10 s for trip 92) because `static/trip-detail/map.js:878-911` eagerly builds one `L.circleMarker` + `toLocaleString` + `bindPopup` per ping — 30,682 for trip 92 — all up front even though the per-point markers are hidden until zoom ≥14. Fix = build them lazily (on first zoom-in / in viewport) and/or use a canvas renderer (`preferCanvas`). Server side is fine (cache read 0.23 s, 3.1 MB JSON). Not yet fixed.

Related: [[feedback_json_ensure_ascii]] (app's `_save_json` writes campgrounds.json etc).
