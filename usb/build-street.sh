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
JAVA_HEAP=1400m       # this box has 3 GB total; planetiler leans on mmap not heap

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
    "$OSMCONVERT" "$raw" -B="$POLY" --complete-ways --complex-ways -o="$out.part"
    mv "$out.part" "$out"
    rm -f "$raw"                       # reclaim space immediately
    echo "  clipped: $(du -h "$out" | cut -f1)  (from $st)"
  done
  rmdir "$RAW" 2>/dev/null || true
fi

# ---- 4. merge ----------------------------------------------------------------
if want merge || want all; then
  if [ ! -s "$MERGED" ]; then
    step "merge $(ls "$CLIP"/*.osm.pbf | wc -l) clipped extracts"
    "$OSMCONVERT" "$CLIP"/*.osm.pbf -o="$MERGED.part"
    mv "$MERGED.part" "$MERGED"
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
    --threads=4 --nodemap_type=sortedtable --storage=mmap
  echo "built: $(du -h "$OUT" | cut -f1)"
  echo "install with:  cp '$OUT' <card>/app/tiles/street.pmtiles"
fi
