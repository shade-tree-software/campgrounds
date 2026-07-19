# Building `street.pmtiles` on a bigger machine

The offline **satellite** layer is already built and installed on the SD card. The
only remaining piece is the offline **street** basemap, `street.pmtiles`, which is
too heavy to render on the small laptop (3 GB RAM → ~10 h and constant GC thrash).
On a normal machine it is well under an hour.

This is a **self-contained** procedure: the build machine needs nothing from the SD
card, and produces exactly **one file** to copy back.

---

## What you need on the build machine

- Linux x86_64, **≥ 16 GB RAM** (8 GB works; 16+ is comfortable), 4+ cores
- **~40 GB free disk** for scratch (the finished file is far smaller)
- Internet (downloads ~6 GB of OSM extracts + ~1.4 GB of planetiler source data)
- `git`, `curl`, `python3`, and a **Java 21+ JRE** (`java -version` to check;
  `sudo apt install openjdk-21-jre-headless` on Debian/Ubuntu/Mint)

Nothing else — the script fetches `osmconvert` and `planetiler.jar` itself.

## Step 1 — get the repo and the trip data

```bash
git clone https://github.com/<your-account>/campgrounds.git ekko
cd ekko
```

The corridor is computed from **your real trip data**, which is gitignored — so the
clone alone is not enough. Copy `trip_data/` (specifically `track_cache/` and
`trips.json`) plus `home.json` from the laptop, e.g. with the existing backup helper:

```bash
# on the laptop
./backup.sh                      # writes backup/ekko-backup-<ts>.tar.gz
# copy that tarball to the build machine, then, in the clone:
tar xzf ekko-backup-<ts>.tar.gz  # restores trip_data/ + home.json in place
```

Sanity check — this must report ~103,000 points, not 0:

```bash
python3 usb/build-tiles.py --repo . --dry-run --max-zoom 8
```

## Step 2 — run the build

```bash
./usb/build-street.sh --repo . --build-dir "$PWD/.streetbuild" --poly-zoom 11
```

That runs the whole pipeline: corridor polygon → download 22 state extracts +
DC → clip each to the corridor → hierarchical merge → planetiler render.

**Give it more memory than the defaults**, which are tuned for the 3 GB laptop.
Edit the two knobs at the top of `usb/build-street.sh` first:

```bash
JAVA_HEAP=8g          # was 1800m
RENDER_THREADS=8      # was 2  (roughly your core count)
```

Notes:
- `--poly-zoom 11` gives a ~29 km corridor each side of every route. The laptop had
  to drop to z12 (~14 km) purely to save time — on a real machine use **11**, or even
  **10** (~58 km) if you want wide off-route context. Wider costs render time, not
  much output size.
- The script is **resumable**: every stage skips work already on disk, so a killed
  run can simply be re-run.
- Expect roughly: clips ~30–60 min (mostly download), merge ~15 min, render 20–60 min.

## Step 3 — copy ONE file to the SD card

The build prints the path when it finishes. Copy it into the card's app:

```bash
cp .streetbuild/street.pmtiles /media/<you>/EKKO/app/tiles/street.pmtiles
```

That is the entire installation step. **No code changes, no config, no restart
flags.** The app detects the file's presence at request time: `_tile_config()`
advertises the vector basemap only when `tiles/street.pmtiles` exists, so the
"Map" layer switches from satellite-imagery-fallback to real vector streets on the
next page load.

Expected size: a few hundred MB to ~1.5 GB. The card has ~35 GB free.

## Step 4 — verify on the card

```bash
cd /media/<you>/EKKO && ./START-EKKO.sh
```

Open any map (trips map, campground map, a trip detail page) **with wifi off** and
confirm the "Map" base layer draws real streets, and "Satellite" still draws imagery.
Zoom past 16 — streets stay sharp (vector overzoom), imagery goes soft (NAIP is
native ~1 m ≈ z16). That difference is expected and correct.

---

## If you want a wider or nationwide street basemap later

Streets are vector, so size tracks OSM data volume, not area — a full-CONUS basemap
is plausibly ~10–15 GB and would fit the card. To do that, replace the per-state
`STATES=(...)` list near the top of `build-street.sh` with a single US extract and
skip the corridor clip:

```bash
curl -O https://download.geofabrik.de/north-america/us-latest.osm.pbf
java -Xmx8g -jar .streetbuild/planetiler.jar \
  --osm_path=us-latest.osm.pbf --output=street.pmtiles --force \
  --minzoom=0 --maxzoom=14 --nodemap_type=sparsearray --storage=mmap
```

That needs ~16 GB RAM and a few hours. **Satellite cannot be scaled the same way** —
it is raster, so full coverage of the 21 swept states would be ~235 GB and CONUS
~950 GB. Widen the satellite ribbon instead (`build-tiles.py --buffer 3` ≈ 12 GB for
a ±1.4 km ribbon), and never fetch past z16 — NAIP has no detail beyond it, so deeper
zooms are pure upscaled blur (z18 alone would add ~37 GB of it).

See `usb/TILE-PIPELINE-DESIGN.md` for the full design and
`project_usb_standalone_edition` in `.claude/memory/` for the build history and the
tooling gotchas already fixed (osmconvert's silent XML default, its refusal to merge
multiple `.pbf`, and NAIP's latency-bound fetch rate).
