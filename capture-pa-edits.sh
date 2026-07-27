#!/usr/bin/env bash
# Capture campground/roadside edits made through the LIVE admin UI, commit them
# here, push, and leave PA's working tree clean again.
#
# Why this exists: campgrounds.json and roadside.json are tracked in git AND
# written by the running app. An edit saved from the campground manage page (or
# a roadside stop added on the map) exists ONLY in PA's working tree — it is in
# no commit and no backup, and the next deploy that touches those files aborts
# on the collision. This is the round trip that closes that loop.
#
# Flow: read the two files down over the READ-ONLY sync key → validate → commit
# → push → tell PA to drop its now-redundant working copy (`reconcile`, which
# only ever discards a file byte-identical to the commit just pushed) → deploy,
# so the live app is serving the committed version.
#
# Usage:
#   ./capture-pa-edits.sh          # capture, commit, push, reconcile, deploy
#   ./capture-pa-edits.sh -n       # dry run: fetch and show the diff only
#   ./capture-pa-edits.sh --no-push  # commit locally, leave PA alone
set -euo pipefail

PA_HOST=shadetreesoftware@ssh.pythonanywhere.com
SYNC_KEY="$HOME/.ssh/pa_sync_ed25519"
DEPLOY_KEY="$HOME/.ssh/pa_deploy_ed25519"
DATA_FILES=(campgrounds.json roadside.json)

HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DRY=0
PUSH=1

while [ $# -gt 0 ]; do
  case "$1" in
    -n|--dry-run) DRY=1; shift ;;
    --no-push)    PUSH=0; shift ;;
    -h|--help)    sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

for k in "$SYNC_KEY" "$DEPLOY_KEY"; do
  [ -f "$k" ] || { echo "error: key $k not found (see CLAUDE.md)" >&2; exit 1; }
done

SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes
          -o PasswordAuthentication=no -o BatchMode=yes)
pa_deploy_ssh() { ssh "${SSH_OPTS[@]}" -i "$DEPLOY_KEY" "$PA_HOST" "$@"; }

cd "$HERE"

# ── Is there anything to capture? ─────────────────────────────────────────────
state="$(pa_deploy_ssh status)"
pa_head="$(sed -n 's/^HEAD=//p' <<<"$state")"
pa_sha="${pa_head%% *}"
pa_dirty="$(sed -n 's/^DIRTY=//p' <<<"$state" | xargs || true)"

if [ -z "$pa_dirty" ]; then
  echo "nothing to capture — PA's working tree is clean"
  exit 0
fi
echo "live edits on PA: $pa_dirty"
echo "PA is at:         $pa_head"

# ── Guards ────────────────────────────────────────────────────────────────────
# 1. Local edits to the same files would be silently overwritten by the copy
#    below, so refuse rather than pick a winner.
if ! git diff --quiet -- "${DATA_FILES[@]}" || ! git diff --cached --quiet -- "${DATA_FILES[@]}"; then
  echo "ABORT: this repo has its own uncommitted changes to those files." >&2
  echo "       Commit or stash them first — capturing would overwrite them." >&2
  exit 1
fi
# 2. PA's HEAD must be an ancestor of ours, and no local commit since then may
#    have touched these files. Otherwise PA's working copy is (its older base +
#    UI edits), and copying it down would REVERT local sweep commits that PA
#    hasn't pulled yet — a silent data loss that looks like a normal capture.
if ! git merge-base --is-ancestor "$pa_sha" HEAD 2>/dev/null; then
  echo "ABORT: PA is at $pa_sha, which this repo doesn't contain. Pull/push first." >&2
  exit 1
fi
if ! git diff --quiet "$pa_sha" HEAD -- "${DATA_FILES[@]}"; then
  echo "ABORT: local commits since $pa_sha already changed those files." >&2
  echo "       Deploy first (./deploy-to-pa.sh), then capture." >&2
  exit 1
fi

# ── Fetch into a staging dir, validate, then move into place ──────────────────
# Never rsync straight over the working copy: a truncated or half-written file
# would land in the repo and the next commit would ship it.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
for f in $pa_dirty; do
  rsync -t -e "ssh ${SSH_OPTS[*]} -i $SYNC_KEY" "$PA_HOST:/$f" "$STAGE/$f"
  # The app writes these with json.dump, so a parse failure means we caught a
  # partial write (or something worse) — either way, don't commit it.
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$STAGE/$f" \
    || { echo "ABORT: $f from PA is not valid JSON — not committing" >&2; exit 1; }
  before=$(python3 -c "import json;print(len(json.load(open('$f'))))" 2>/dev/null || echo '?')
  after=$(python3 -c "import json;print(len(json.load(open('$STAGE/$f'))))")
  echo "  $f: $before -> $after entries"
done

for f in $pa_dirty; do cp "$STAGE/$f" "$f"; done

if git diff --quiet -- "${DATA_FILES[@]}"; then
  echo "nothing to capture — the live edits are already in this commit"
  git checkout -- "${DATA_FILES[@]}" 2>/dev/null || true
  exit 0
fi

echo
git --no-pager diff --stat -- "${DATA_FILES[@]}"

if [ "$DRY" -eq 1 ]; then
  echo
  echo "== dry run: reverting the local copy, nothing committed =="
  git checkout -- "${DATA_FILES[@]}"
  exit 0
fi

# ── Commit + push ─────────────────────────────────────────────────────────────
git add -- "${DATA_FILES[@]}"
git commit -q -m "Capture campground edits made in the live UI

Saved through the admin UI on PythonAnywhere, where they existed only in
the working tree — in no commit and no backup. Captured verbatim; the
content is exactly what the live app wrote.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
echo "committed: $(git log --oneline -1)"

if [ "$PUSH" -eq 0 ]; then
  echo "--no-push: stopping here. PA still has the edits in its working tree."
  exit 0
fi

git push -q origin master
echo "pushed."

# ── Put PA back in sync ───────────────────────────────────────────────────────
# reconcile drops PA's working copy only where it is byte-identical to what we
# just pushed (it verifies the blob hash), so it cannot lose an edit saved in
# the meantime — that one simply stays dirty and the next run captures it.
echo "== reconciling PA =="
pa_deploy_ssh reconcile
"$HERE/deploy-to-pa.sh"
