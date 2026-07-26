#!/usr/bin/env bash
# Incrementally PULL trip data and/or photos from the live PythonAnywhere app.
#
# backup.sh/restore.sh move the whole dataset as a tarball, which is the right
# tool for seeding a new machine but wasteful for the common case (a few new
# photos, an edited trip). This transfers only what changed, and is the normal
# way to refresh a laptop or the USB/SD standalone edition.
#
# Auth: your PythonAnywhere password in PA_PW (gitignored .env), fed to ssh via
# pa-ask-pass.sh — no sshpass, no sudo, and the password never appears in the
# process list or in this script's output.
#
# Usage:
#   ./sync-from-pa.sh                 # data + photos into this repo
#   ./sync-from-pa.sh --data          # trip_data/ only (small, fast)
#   ./sync-from-pa.sh --photos        # photo_uploads/ only
#   ./sync-from-pa.sh -n              # dry run: show what would transfer
#   ./sync-from-pa.sh --dest /media/andrew/EKKO/app     # refresh the SD card
#   ./sync-from-pa.sh --delete        # also remove local files gone from PA
set -euo pipefail

PA_HOST=shadetreesoftware@ssh.pythonanywhere.com
PA_ROOT=/home/shadetreesoftware/campgrounds
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DEST="$HERE"
DO_DATA=0
DO_PHOTOS=0
DRY=()
DEL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --data)        DO_DATA=1; shift ;;
    --photos)      DO_PHOTOS=1; shift ;;
    --dest)        DEST="$2"; shift 2 ;;
    -n|--dry-run)  DRY=(--dry-run); shift ;;
    # --force lets --delete replace a directory with a non-directory. It does NOT
    # help with a dir whose only remaining contents are excluded (.thumbs/,
    # .views/, .trash/) — an exclude also protects those from deletion, so rsync warns
    # "cannot delete non-empty directory" and moves on. reap_orphaned_dirs()
    # below cleans those up afterwards.
    --delete)      DEL=(--delete --force); shift ;;
    -h|--help)     sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
# Default: both halves.
if [ $DO_DATA -eq 0 ] && [ $DO_PHOTOS -eq 0 ]; then DO_DATA=1; DO_PHOTOS=1; fi

[ -d "$DEST" ] || { echo "error: --dest '$DEST' does not exist" >&2; exit 1; }

# Feed the password to ssh without a TTY prompt. SSH_ASKPASS_REQUIRE=force needs
# OpenSSH 8.4+; setsid detaches from the terminal so ssh actually consults it.
export SSH_ASKPASS="$HERE/pa-ask-pass.sh"
export SSH_ASKPASS_REQUIRE=force
[ -x "$SSH_ASKPASS" ] || { echo "error: $SSH_ASKPASS missing or not executable" >&2; exit 1; }

# accept-new: pin PA's host key on first use, but still fail on a CHANGED key
# (a silent StrictHostKeyChecking=no would accept an impostor).
SSH_CMD="ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no"

# -rlt keeps mtimes, which matters beyond tidiness: the app's thumbnail cache and
# track cache are mtime-keyed, so clobbering timestamps would silently invalidate
# them. Deliberately NOT -a: -o/-g (owner/group) need root and only emit noise.
RSYNC_OPTS=(-rltvz --partial --human-readable --info=progress2 "${DRY[@]}" "${DEL[@]}")

# rsync's output is tee'd here so reap_orphaned_dirs() can read its warnings.
RSYNC_LOG=$(mktemp)
trap 'rm -f "$RSYNC_LOG"' EXIT

# Directories we exclude from the transfer because they regenerate on demand.
# Their presence is what blocks rsync from deleting a directory that has gone
# away upstream.
CACHE_DIRS=(.thumbs .views .trash __pycache__)

# When a directory vanishes from PA but still holds one of those caches locally,
# rsync can't remove it and warns "cannot delete non-empty directory: 56/events/50"
# on every single sync. The warning is harmless — the directory is gone upstream
# and what's left is regenerable — but it recurs forever and buries real output.
# --delete-excluded would silence it by wiping every live thumbnail cache too,
# which is far too broad, so instead finish rsync's job by hand: for each
# directory it named, delete it only if everything still inside is one of those
# caches. Anything else means the leftovers are real and the dir stays.
reap_orphaned_dirs() {          # reap_orphaned_dirs <target> <label>
  local target="$1" label="$2" rel dir leftover n
  local keep=()
  [ ${#DEL[@]} -gt 0 ] || return 0     # nothing was being deleted
  [ ${#DRY[@]} -eq 0 ] || return 0     # a dry run must not touch disk

  for n in "${CACHE_DIRS[@]}"; do keep+=(! -name "$n"); done

  # tr: --info=progress2 redraws with \r, so a warning can share a line with the
  # progress counter. sort -ru: deepest paths first, so a stale child is already
  # gone by the time its parent is considered.
  while IFS= read -r rel; do
    [ -n "$rel" ] || continue
    dir="$target/$rel"
    [ -d "$dir" ] || continue
    leftover=$(find "$dir" -mindepth 1 -maxdepth 1 "${keep[@]}" -print -quit)
    [ -z "$leftover" ] || continue     # real content: not ours to remove
    rm -rf -- "$dir"
    echo "  removed orphaned cache dir: $label/$rel"
    # The parent may now be empty as well (56/events, once its last stale child
    # goes). rmdir climbs only while each level is genuinely empty.
    rmdir -p --ignore-fail-on-non-empty "$(dirname "$dir")" 2>/dev/null || true
  done < <(tr '\r' '\n' < "$RSYNC_LOG" |
           sed -n 's/.*cannot delete non-empty directory: //p' | sort -ru)
}

pull() {                      # pull <remote-subdir> <local-subdir> [extra excludes...]
  local remote="$1" local_sub="$2"; shift 2
  local target="$DEST/$local_sub"
  mkdir -p "$target"
  echo
  echo "=== $local_sub  <-  PA:$remote ==="

  # Preflight: a full photo pull is ~7 GB, which is more than some destinations
  # have free (this dev laptop has ~4 GB on /). Filling a root filesystem is a
  # genuinely bad failure, so price the transfer first and refuse if it won't
  # fit. Skipped when the caller already asked for a dry run.
  if [ ${#DRY[@]} -eq 0 ]; then
    local need avail
    # NOTE: --no-human-readable is load-bearing. With rsync's -h, the stats line
    # reads "Total transferred file size: 4.45G bytes"; stripping non-digits then
    # yields 445 — a 10-million-fold underestimate that silently defeats the
    # space check (observed: it happily started a 7 GB pull onto a 4 GB disk).
    need=$(rsync -rltz --dry-run --stats --no-human-readable "${DEL[@]}" "$@" \
             -e "$SSH_CMD" "$PA_HOST:$PA_ROOT/$remote/" "$target/" 2>/dev/null \
           | awk -F': *' '/Total transferred file size/{gsub(/[^0-9]/,"",$2); print $2; exit}')
    avail=$(df -B1 --output=avail "$target" | tail -1)
    if [ -n "$need" ] && [ "$need" -gt 0 ]; then
      echo "  to transfer: $(numfmt --to=iec "$need")   free at destination: $(numfmt --to=iec "$avail")"
      # Keep a 500 MB cushion so we don't wedge the filesystem at 100%.
      if [ "$need" -gt $((avail - 500*1024*1024)) ]; then
        echo "  ERROR: not enough free space at $target." >&2
        echo "         Free space, or use --dest to target a bigger volume" >&2
        echo "         (e.g. --dest /media/andrew/EKKO/app for the SD card)." >&2
        exit 1
      fi
    fi
    # NOTE: do NOT early-return here when $need is empty/0. The preflight only
    # prices FILE TRANSFERS (bytes to send), not DELETIONS — and it can also come
    # back empty on a transient preflight-rsync hiccup. Treating either as "up to
    # date" silently skipped the real rsync below, so pending --delete removals
    # (and metadata-only updates) never applied. Always fall through to rsync; it
    # is the source of truth for what actually changes.
  fi

  # pipefail is set, so a failing rsync still aborts despite the tee.
  rsync "${RSYNC_OPTS[@]}" "$@" -e "$SSH_CMD" \
    "$PA_HOST:$PA_ROOT/$remote/" "$target/" 2>&1 | tee "$RSYNC_LOG"

  reap_orphaned_dirs "$target" "$local_sub"
}

if [ $DO_DATA -eq 1 ]; then
  # secret_key and dev_cert.* are deliberately machine-local: pulling PA's
  # session secret would invalidate local logins and spread a production secret,
  # and the dev cert is this machine's self-signed HTTPS cert.
  pull trip_data trip_data \
    --exclude 'secret_key' --exclude 'dev_cert.*' --exclude '__pycache__/'
fi

if [ $DO_PHOTOS -eq 1 ]; then
  # .thumbs/ and .views/ are regenerated on demand from the originals (and are
  # large), .trash/
  # holds already-deleted photos pending purge. Neither is worth the bandwidth.
  pull photo_uploads photo_uploads \
    --exclude '.thumbs/' --exclude '.views/' --exclude '.trash/'
fi

echo
if [ ${#DRY[@]} -gt 0 ]; then
  echo "dry run — nothing was written. Re-run without -n to transfer."
else
  echo "done. Synced into: $DEST"
  [ ${#DEL[@]} -eq 0 ] && echo "(local-only files were kept; pass --delete to mirror PA exactly)"
fi
