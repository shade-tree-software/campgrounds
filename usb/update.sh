#!/usr/bin/env bash
#
# update.sh — pull the latest app code from GitHub into ./app.
#
# REQUIRES INTERNET. The repo is public, so no login is needed for a pull.
# After pulling, it re-syncs Python dependencies in case new code needs them.
#
set -euo pipefail

HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PY="$HERE/python/bin/python3"
APP="$HERE/app"
REQ="$HERE/requirements-ekko.txt"

if [ ! -d "$APP/.git" ]; then
  echo "ERROR: $APP is not a git checkout." >&2
  exit 1
fi

# Put the portable Python first on PATH so any git hooks / helper scripts that
# call `python3` use ours (the host may not have Python at all).
export PATH="$HERE/python/bin:$PATH"

cd "$APP"
echo ">> Fetching latest code..."
git pull --ff-only origin master

if [ -x "$PY" ]; then
  echo ">> Re-syncing dependencies (in case new code needs them)..."
  "$PY" -m pip install -q -r "$REQ" || \
    echo "WARN: dependency sync failed (offline?). App code was still updated."
fi

echo ">> Update complete."
