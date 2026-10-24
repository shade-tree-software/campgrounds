#!/bin/sh
# setup.sh SCRATCH: copy the helpers into a new session's scratchpad so the briefs' paths resolve.
set -e
S="$1"; K="$(cd "$(dirname "$0")" && pwd)"
[ -n "$S" ] || { echo "usage: setup.sh SCRATCH_DIR" >&2; exit 2; }
mkdir -p "$S/helpers"; cp "$K"/helpers/*.py "$S/helpers/"; touch "$S/headless-browser.lock"
echo "helpers in $S/helpers"
