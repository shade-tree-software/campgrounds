#!/usr/bin/env bash
#
# backup.sh — bundle EKKO Trips' gitignored "database" into one tarball.
#
# Packages exactly the data that is NOT in git and NOT regenerable:
#   users.json, home.json, and trip_data/*.json (trips, captions,
#   photo_order, photo_uploaders, share_tokens) + trip_data/access_log.jsonl
#   + trip_data/track_cache/.
#
# Deliberately EXCLUDED:
#   - campgrounds.json          (tracked in git — comes down with a pull)
#   - photo_uploads/            (photos; huge — pass --with-photos to include)
#   - trip_data/secret_key,
#     trip_data/dev_cert.{crt,key} (machine-local session key / dev TLS cert)
#   - .thumbs/ and .trash/      (regenerated thumbnails / pending-purge deletes)
#   - .env                      (secrets — each host has its own)
#
# Usage:
#   ./backup.sh                 # data-only bundle -> backup/ekko-backup-<ts>.tar.gz
#   ./backup.sh --with-photos   # also include photo_uploads/ (minus thumbs/trash)
#   ./backup.sh -o /path/out.tar.gz   # write to a specific path
#
# Restore with ./restore.sh <tarball>.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO"

WITH_PHOTOS=0
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-photos) WITH_PHOTOS=1; shift ;;
    -o|--output)   OUT="${2:-}"; shift 2 ;;
    -h|--help)
      sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "backup.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

# Timestamp is filesystem-derived (no reliance on any app state).
TS="$(date +%Y%m%d-%H%M%S)"
if [[ -z "$OUT" ]]; then
  mkdir -p "$REPO/backup"
  OUT="$REPO/backup/ekko-backup-${TS}.tar.gz"
fi

# Candidate members (relative to repo root). Only existing ones are archived,
# so a fresh install missing e.g. share_tokens.json still backs up cleanly.
CANDIDATES=(
  users.json
  home.json
  trip_data/trips.json
  trip_data/captions.json
  trip_data/photo_order.json
  trip_data/photo_uploaders.json
  trip_data/share_tokens.json
  trip_data/access_log.jsonl
  trip_data/track_cache
)
[[ "$WITH_PHOTOS" -eq 1 ]] && CANDIDATES+=(photo_uploads)

MEMBERS=()
for m in "${CANDIDATES[@]}"; do
  if [[ -e "$m" ]]; then
    MEMBERS+=("$m")
  else
    echo "  (skip, not present) $m"
  fi
done

if [[ "${#MEMBERS[@]}" -eq 0 ]]; then
  echo "backup.sh: nothing to back up — no data files found under $REPO" >&2
  exit 1
fi

# Regenerable/local paths never belong in the bundle even when a parent dir
# (track_cache, photo_uploads) is included.
tar -czf "$OUT" \
  --exclude='*/.thumbs' --exclude='*/.thumbs/*' \
  --exclude='*/.trash'  --exclude='*/.trash/*' \
  --exclude='trip_data/secret_key' \
  --exclude='trip_data/dev_cert.crt' \
  --exclude='trip_data/dev_cert.key' \
  -C "$REPO" "${MEMBERS[@]}"

SIZE="$(du -h "$OUT" | cut -f1)"
echo "Backup written: $OUT  ($SIZE)"
echo "Included:"
printf '  %s\n' "${MEMBERS[@]}"
[[ "$WITH_PHOTOS" -eq 0 ]] && echo "Photos NOT included (pass --with-photos to add photo_uploads/)."
