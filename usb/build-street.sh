#!/usr/bin/env bash
# Build the offline VECTOR STREET basemap (street.pmtiles) for the EKKO USB
# standalone edition — Option A of usb/TILE-PIPELINE-DESIGN.md.
#
# Pipeline:
#   1. build-tiles.py --emit-poly  -> corridor.poly (the trip corridor as an
#      Osmosis polygon, dissolved into per-row rectangles)
#   2. download each covered state's Geofabrik .osm.pbf extract (ODbL)
#   3. osmconvert -B=corridor.poly  -> clip each state to the corridor, then
#      DELETE the raw extract (they are big; the clip is what we keep)
#   4. osmconvert merges the clips into one corridor.osm.pbf
#   5. planetiler renders it to street.pmtiles (OpenMapTiles schema, z0-14;
#      sparsearray nodemap: faster random node lookups than sortedtable in pass2,
#      and the extra size lands in the mmap'd file rather than the heap;
#      protomaps-leaflet overzooms past 14, so 14 is plenty)
#
# Everything is staged under <card>/.build so the tiny local disk isn't used;
# planetiler's temp dir goes there too. Every stage is RESUMABLE — existing
# outputs are skipped, so a killed run just re-runs.
#
# Usage:  ./build-street.sh [--build-dir DIR] [--repo DIR] [--poly-zoom N]
#                           [--stage download|clip|merge|render|all]
set -euo pipefail

BUILD_DIR=/media/andrew/EKKO/.build
REPO=/media/andrew/EKKO/app
POLY_ZOOM=11          # z11 +/-1 tile => a ~19 km corridor each side of the route
STAGE=all
JAVA_HEAP=1800m       # 3 GB box: 1400m OOM'd (300M sortedtable index + 4 threads of
                      # feature buffers). Leave ~1 GB for the OS page cache — planetiler
                      # mmaps ~3.5 GB of node locations and thrashes without it.
RENDER_THREADS=2      # heap, not CPU, is the binding constraint on this 3 GB box:
                      # at 3 threads osm_pass2 sat at postGC 1.7G/1.8G and crawled at
                      # ~600 ways/s. Fewer in-flight feature buffers = less GC pressure.

while [ $# -gt 0 ]; do
  case "$1" in
    --build-dir) BUILD_DIR="$2"; shift 2 ;;
    --repo)      REPO="$2"; shift 2 ;;
    --poly-zoom) POLY_ZOOM="$2"; shift 2 ;;
    --stage)     STAGE="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# States the trip corridor touches, from a point-in-polygon classification of
# the corridor points (see the sweep notes). Vermont + Rhode Island are included
# defensively: the corridor clips their borders and the extracts are tiny.
STATES=(
  pennsylvania virginia maryland florida south-carolina west-virginia
  new-york north-carolina georgia michigan maine delaware massachusetts
  wisconsin ohio connecticut new-jersey indiana illinois new-hampshire
  district-of-columbia vermont rhode-island
)
GEOFABRIK=https://download.geofabrik.de/north-america/us

HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
OSMCONVERT="$BUILD_DIR/osmconvert"
PLANETILER="$BUILD_DIR/planetiler.jar"
JAVA="$BUILD_DIR/jdk-21.0.11+10-jre/bin/java"
POLY="$BUILD_DIR/corridor.poly"
RAW="$BUILD_DIR/raw"
CLIP="$BUILD_DIR/clip"
MERGED="$BUILD_DIR/corridor.osm.pbf"
OUT="$BUILD_DIR/street.pmtiles"

mkdir -p "$RAW" "$CLIP" "$BUILD_DIR/pltmp"

step() { echo; echo "=== $* ==="; }
want() { [ "$STAGE" = all ] || [ "$STAGE" = "$1" ]; }

# ---- 0. bootstrap the toolchain ----------------------------------------------
# Fetch osmconvert + planetiler if this build dir doesn't have them yet, so the
# script runs on a fresh machine (see usb/BUILD-STREET-ON-BIG-MACHINE.md) and not
# just the one where they were staged by hand.
if [ ! -x "$OSMCONVERT" ]; then
  step "bootstrap osmconvert"
  src="$BUILD_DIR/osmconvert.c"
  if [ ! -s "$src" ]; then
    curl -fL -o "$src" http://m.m.i24.cc/osmconvert.c \
      || curl -fL -o "$src" https://raw.githubusercontent.com/UlmApi/osmconvert/master/osmconvert.c
  fi
  cc -x c "$src" -lz -O3 -o "$OSMCONVERT"     # needs zlib headers (zlib1g-dev)
fi
if [ ! -s "$PLANETILER" ]; then
  step "bootstrap planetiler"
  curl -fL -o "$PLANETILER" \
    https://github.com/onthegomap/planetiler/releases/latest/download/planetiler.jar
fi
# Prefer a JRE bundled in the build dir (the USB build box has one); otherwise use
# whatever java is on PATH. Planetiler needs 21+.
if [ ! -x "$JAVA" ]; then
  JAVA="$(command -v java || true)"
  [ -x "$JAVA" ] || { echo "ERROR: no java found. Install a JRE 21+ (e.g. apt install openjdk-21-jre-headless)" >&2; exit 1; }
fi

# ---- 1. corridor polygon -----------------------------------------------------
# Unconditional: every later stage clips/renders against this polygon, so it must
# match the requested --poly-zoom even when resuming into a single --stage.
step "corridor polygon (z$POLY_ZOOM)"
python3 "$HERE/build-tiles.py" --repo "$REPO" --emit-poly "$POLY" --poly-zoom "$POLY_ZOOM"

# ---- 2+3. download & clip (raw deleted right after its clip) ------------------
if want download || want clip || want all; then
  for st in "${STATES[@]}"; do
    out="$CLIP/$st.osm.pbf"
    [ -s "$out" ] && { echo "clip present, skip: $st"; continue; }
    step "$st"
    raw="$RAW/$st-latest.osm.pbf"
    if [ ! -s "$raw" ]; then
      curl -fL --retry 3 --retry-delay 5 -o "$raw.part" "$GEOFABRIK/$st-latest.osm.pbf"
      mv "$raw.part" "$raw"
    fi
    # --out-pbf is REQUIRED: osmconvert defaults to uncompressed .osm XML no
    # matter what the -o= extension says, which is ~20x the size (a 326 MB PA
    # extract clipped to 6.3 GB of XML before this flag was added).
    "$OSMCONVERT" "$raw" -B="$POLY" --complete-ways --complex-ways \
      --out-pbf -o="$out.part"
    mv "$out.part" "$out"
    rm -f "$raw"                       # reclaim space immediately
    echo "  clipped: $(du -h "$out" | cut -f1)  (from $st)"
  done
  rmdir "$RAW" 2>/dev/null || true
fi

# ---- 4. merge ----------------------------------------------------------------
if want merge || want all; then
  if [ ! -s "$MERGED" ]; then
    # osmconvert refuses more than one .pbf input ("more than one .pbf input
    # file is not allowed") — it can only merge .o5m/.osm. So convert each clip
    # to .o5m first, merge those, and emit the result as .pbf for planetiler.
    step "merge $(ls "$CLIP"/*.osm.pbf | wc -l) clipped extracts (via .o5m)"
    for f in "$CLIP"/*.osm.pbf; do
      o5m="${f%.osm.pbf}.o5m"
      [ -s "$o5m" ] && continue
      echo "  -> o5m: $(basename "$f")"
      "$OSMCONVERT" "$f" --out-o5m -o="$o5m.part" && mv "$o5m.part" "$o5m"
    done
    # Merge HIERARCHICALLY, in groups. Handing osmconvert all 23 .o5m at once
    # got OOM-killed on this 3 GB box (the NAIP fetch runs concurrently), and a
    # sequential fold would rewrite the whole accumulator 23 times (~40 GB of
    # card I/O). Groups of 6 cap peak inputs while costing only ~2x data moved.
    mapfile -t all < <(ls "$CLIP"/*.o5m | grep -v '/_group')
    groups=(); i=0; g=0
    while [ $i -lt ${#all[@]} ]; do
      batch=("${all[@]:$i:6}")
      gfile="$CLIP/_group$g.o5m"
      if [ ! -s "$gfile" ]; then                     # resumable
        echo "  -> group $g (${#batch[@]} files)"
        "$OSMCONVERT" "${batch[@]}" --out-o5m -o="$gfile.part"
        mv "$gfile.part" "$gfile"
      fi
      groups+=("$gfile"); i=$((i + 6)); g=$((g + 1))
    done
    echo "  -> final merge of ${#groups[@]} groups"
    "$OSMCONVERT" "${groups[@]}" --out-pbf -o="$MERGED.part"
    mv "$MERGED.part" "$MERGED"
    rm -f "$CLIP"/*.o5m           # o5m is ~1.5x the pbf size; groups go too
  fi
  echo "merged: $(du -h "$MERGED" | cut -f1)"
fi

# ---- 5. render ---------------------------------------------------------------
if want render || want all; then
  step "planetiler render -> street.pmtiles"
  "$JAVA" -Xmx$JAVA_HEAP -jar "$PLANETILER" \
    --osm_path="$MERGED" \
    --polygon="$POLY" \
    --download_dir="$BUILD_DIR/data/sources" \
    --tmpdir="$BUILD_DIR/pltmp" \
    --output="$OUT" --force \
    --minzoom=0 --maxzoom=14 \
    --threads=$RENDER_THREADS --nodemap_type=sparsearray \
    --storage=mmap --nodemap_storage=mmap --nodemap_madvise=true
  echo "built: $(du -h "$OUT" | cut -f1)"
  echo "install with:  cp '$OUT' <card>/app/tiles/street.pmtiles"
fi
