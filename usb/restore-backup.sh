#!/usr/bin/env bash
#
# restore-backup.sh — restore an EKKO Trips data bundle (ekko-backup-*.tar.gz)
# onto this stick. Works offline.
#
# This is a thin wrapper around the app's own ./app/restore.sh: it puts the
# portable Python on PATH (restore.sh validates JSON with python3) and then
# hands off. restore.sh snapshots the current data to app/backup/ first, so a
# bad restore is reversible.
#
#   Usage:  ./restore-backup.sh /path/to/ekko-backup-YYYYMMDD-HHMMSS.tar.gz
#           ./restore-backup.sh -y <tarball>     # skip confirmation
#
# Stop the app (Ctrl+C in the START-EKKO window) before restoring.
#
set -euo pipefail

HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
APP="$HERE/app"

if [ ! -x "$APP/restore.sh" ]; then
  echo "ERROR: $APP/restore.sh not found." >&2
  exit 1
fi
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [-y] <ekko-backup-XXXXXXXX-XXXXXX.tar.gz>" >&2
  exit 2
fi

export PATH="$HERE/python/bin:$PATH"

# Resolve any positional tarball path to absolute (restore.sh cd's into $APP).
args=()
for a in "$@"; do
  case "$a" in
    -*) args+=("$a") ;;
    *)  args+=("$(readlink -f "$a")") ;;
  esac
done

cd "$APP"
exec ./restore.sh "${args[@]}"
