#!/usr/bin/env bash
#
# restore.sh — restore an EKKO Trips data bundle made by ./backup.sh.
#
# Safety model:
#   1. Verifies the tarball looks like an EKKO bundle (contains trips.json).
#   2. Snapshots the CURRENT data into backup/pre-restore-<ts>.tar.gz first,
#      so a bad restore is always reversible.
#   3. Extracts the bundle over the repo (paths are repo-root-relative).
#   4. Validates every restored *.json parses, and fails loudly if not.
#
# Usage:
#   ./restore.sh backup/ekko-backup-20260711-101500.tar.gz
#   ./restore.sh -y <tarball>     # skip the confirmation prompt
#
# NOTE: this OVERWRITES users.json / home.json / trip_data JSON with the
# bundle's versions. Stop the running app first so nothing writes mid-restore.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO"

ASSUME_YES=0
ARCHIVE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes) ASSUME_YES=1; shift ;;
    -h|--help)
      sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    -*) echo "restore.sh: unknown option '$1'" >&2; exit 2 ;;
    *)  ARCHIVE="$1"; shift ;;
  esac
done

if [[ -z "$ARCHIVE" ]]; then
  echo "restore.sh: give the bundle to restore, e.g. ./restore.sh backup/ekko-backup-<ts>.tar.gz" >&2
  exit 2
fi
if [[ ! -f "$ARCHIVE" ]]; then
  echo "restore.sh: no such file: $ARCHIVE" >&2
  exit 1
fi

# Sanity-check the tarball before touching anything.
LISTING="$(tar -tzf "$ARCHIVE")"
if ! grep -q '^trip_data/trips\.json$' <<<"$LISTING"; then
  echo "restore.sh: '$ARCHIVE' doesn't contain trip_data/trips.json — refusing" >&2
  echo "            (is this really an EKKO backup bundle?)" >&2
  exit 1
fi

echo "About to restore from: $ARCHIVE"
echo "Members:"
sed 's/^/  /' <<<"$LISTING" | head -20
[[ "$(wc -l <<<"$LISTING")" -gt 20 ]] && echo "  … ($(wc -l <<<"$LISTING") entries total)"
echo
echo "This OVERWRITES the current data in $REPO."

if [[ "$ASSUME_YES" -ne 1 ]]; then
  read -r -p "Proceed? [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }
fi

# 1) Snapshot current state so the restore is reversible.
TS="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REPO/backup"
SAFETY="$REPO/backup/pre-restore-${TS}.tar.gz"
PRESERVE=()
for m in users.json home.json \
         trip_data/family.json \
         trip_data/trips.json trip_data/captions.json \
         trip_data/photo_order.json trip_data/photo_uploaders.json \
         trip_data/photo_favorites.json trip_data/photo_people.json \
         trip_data/share_tokens.json trip_data/access_log.jsonl \
         trip_data/track_cache; do
  [[ -e "$m" ]] && PRESERVE+=("$m")
done
if [[ "${#PRESERVE[@]}" -gt 0 ]]; then
  tar -czf "$SAFETY" -C "$REPO" "${PRESERVE[@]}"
  echo "Current data snapshotted to: $SAFETY"
else
  echo "No existing data to snapshot (fresh install)."
fi

# 2) Extract the bundle over the repo.
tar -xzf "$ARCHIVE" -C "$REPO"
echo "Extracted bundle."

# 3) Validate every restored JSON parses.
JSON_MEMBERS="$(grep -E '\.json$' <<<"$LISTING" || true)"
BAD=0
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$REPO/$f" 2>/dev/null; then
    echo "  INVALID JSON: $f" >&2
    BAD=1
  fi
done <<<"$JSON_MEMBERS"

if [[ "$BAD" -ne 0 ]]; then
  echo "restore.sh: one or more restored files are not valid JSON." >&2
  [[ "${#PRESERVE[@]}" -gt 0 ]] && \
    echo "            Roll back with: ./restore.sh -y $SAFETY" >&2
  exit 1
fi

echo "Restore complete — all JSON validated. Restart the app to pick it up."
