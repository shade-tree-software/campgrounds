#!/usr/bin/env bash
# Incrementally PULL trip data and/or photos from the live PythonAnywhere app.
#
# backup.sh/restore.sh move the whole dataset as a tarball, which is the right
# tool for seeding a new machine but wasteful for the common case (a few new
# photos, an edited trip). This transfers only what changed, and is the normal
# way to refresh a laptop or the USB/SD standalone edition.
#
# Auth: a dedicated SSH key, ~/.ssh/pa_sync_ed25519. On PA that key is pinned to
# `command="/usr/bin/rrsync -ro /home/shadetreesoftware/campgrounds",restrict`, so
# it can ONLY read files under the repo — it cannot get a shell and cannot write
# (verified: an upload is refused with "sending to read-only server"). No account
# password is stored anywhere on this machine.
#
# Usage:
#   ./sync-from-pa.sh                 # data + photos into this repo
#   ./sync-from-pa.sh --data          # trip_data/ only (small, fast)
#   ./sync-from-pa.sh --photos        # photo_uploads/ only (every trip)
#   ./sync-from-pa.sh --photos 92     # photos for trip 92 only (ids repeatable)
#   ./sync-from-pa.sh -n              # dry run: show what would transfer
#   ./sync-from-pa.sh --dest /media/andrew/EKKO/app     # refresh the SD card
#   ./sync-from-pa.sh --delete        # also remove local files gone from PA
set -euo pipefail

PA_HOST=shadetreesoftware@ssh.pythonanywhere.com
# Paths are relative to the directory rrsync confines the key to, so they carry
# no /home/... prefix — that root lives in authorized_keys on PA, not here.
PA_KEY="$HOME/.ssh/pa_sync_ed25519"
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DEST="$HERE"
DO_DATA=0
DO_PHOTOS=0
TRIPS=()
DRY=()
DEL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --data)        DO_DATA=1; shift ;;
    # Bare --photos means the whole library; any trip ids that follow narrow it
    # to those trips. One flag rather than two because "--photos --trip 92" read
    # as "all photos AND trip 92" while actually meaning only trip 92.
    #
    # Photo directories are keyed by TRIP ID -- photo_uploads/<trip_id>/... --
    # which is the number in the trip's own URL (/trips/92), not the display
    # "Trip N" number (that one is computed from chronological position and
    # shifts whenever a trip is added).
    #
    # Consuming only all-digit tokens is unambiguous here because the script
    # takes no positional arguments -- a bare number can't mean anything else.
    --photos)      DO_PHOTOS=1; shift
                   while [ $# -gt 0 ]; do
                     case "$1" in
                       ''|*[!0-9]*) break ;;
                       *) TRIPS+=("$1"); shift ;;
                     esac
                   done ;;
    --dest)        DEST="$2"; shift 2 ;;
    -n|--dry-run)  DRY=(--dry-run); shift ;;
    # --force lets --delete replace a directory with a non-directory. It does NOT
    # help with a dir whose only remaining contents are excluded (.thumbs/,
    # .views/, .trash/) — an exclude also protects those from deletion, so rsync warns
    # "cannot delete non-empty directory" and moves on. reap_orphaned_dirs()
    # below cleans those up afterwards.
    --delete)      DEL=(--delete --force); shift ;;
    -h|--help)     sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
# Default: both halves.
if [ $DO_DATA -eq 0 ] && [ $DO_PHOTOS -eq 0 ]; then DO_DATA=1; DO_PHOTOS=1; fi

[ -d "$DEST" ] || { echo "error: --dest '$DEST' does not exist" >&2; exit 1; }

[ -f "$PA_KEY" ] || { echo "error: sync key $PA_KEY not found (see README-flask-app.md)" >&2; exit 1; }

# accept-new: pin PA's host key on first use, but still fail on a CHANGED key
# (a silent StrictHostKeyChecking=no would accept an impostor).
# BatchMode + PasswordAuthentication=no: if the key is ever rejected this must
# fail immediately, not fall back to prompting for the account password.
SSH_CMD="ssh -o StrictHostKeyChecking=accept-new -i $PA_KEY -o IdentitiesOnly=yes -o PasswordAuthentication=no -o BatchMode=yes"

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

# Does a directory exist on PA? --list-only is a read, so it works over the
# read-only rrsync key. Used to turn a typo'd trip id into a clear error instead
# of an rsync "No such file or directory" after a local directory was created.
remote_has() {                # remote_has <remote-subdir>
  rsync --list-only -e "$SSH_CMD" "$PA_HOST:/$1/" >/dev/null 2>&1
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
             -e "$SSH_CMD" "$PA_HOST:/$remote/" "$target/" 2>/dev/null \
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
    "$PA_HOST:/$remote/" "$target/" 2>&1 | tee "$RSYNC_LOG"

  reap_orphaned_dirs "$target" "$local_sub"
}

if [ $DO_DATA -eq 1 ]; then
  # secret_key and dev_cert.* are deliberately machine-local: pulling PA's
  # session secret would invalidate local logins and spread a production secret,
  # and the dev cert is this machine's self-signed HTTPS cert.
  #
  # This is also the ONLY path by which family.json (relatives' addresses, kept
  # out of the public repo) comes down from PA. capture-pa-edits.sh handles live
  # manage-page edits to the *tracked* location file, campgrounds.json, via git;
  # a family entry added or edited in that same UI is gitignored, so it rides
  # here instead — which is why family.json lives under trip_data/.
  # models/ holds downloaded model weights (YuNet for detect_people.py). They
  # re-download on demand wherever they're needed, so they are never worth the
  # transfer.
  # models/ and geonames/ are per-host caches that regenerate on demand (the
  # YuNet weights; the GeoNames gazetteer). place_context.json is derived from
  # trips.json by backfill_place_context.py and is likewise per-host — without
  # these excludes a --delete sync wipes whichever ones this machine built and
  # PA happens not to have, which is exactly what happened the first time.
  #
  # day_rollups.json is the sharper case: it exists ONLY here, because the API
  # key is local and PA cannot write it, and it cost real money to generate. A
  # --delete sync deleted a whole trip's drafted prose before this exclude
  # existed. It is also in backup.sh now, for the same reason.
  pull trip_data trip_data \
    --exclude 'secret_key' --exclude 'dev_cert.*' --exclude '__pycache__/' \
    --exclude 'models/' --exclude 'geonames/' --exclude 'place_context.json' \
    --exclude 'day_rollups.json' --exclude '*.corrupt-*' --exclude '*.tmp'

fi

if [ $DO_PHOTOS -eq 1 ]; then
  # .thumbs/ and .views/ are regenerated on demand from the originals (and are
  # large), .trash/
  # holds already-deleted photos pending purge. Neither is worth the bandwidth.
  PHOTO_EXCLUDES=(--exclude '.thumbs/' --exclude '.views/' --exclude '.trash/')
  if [ ${#TRIPS[@]} -gt 0 ]; then
    # One trip is a few dozen MB against ~7 GB for the library, so this is the
    # cheap way to pick up the photos from the trip you just got home from.
    # Pulling the subdirectory itself (rather than filtering the whole tree)
    # keeps the space preflight, --delete and the orphan reap scoped to it too.
    for t in "${TRIPS[@]}"; do
      remote_has "photo_uploads/$t" || {
        echo "error: PA has no photo_uploads/$t — is $t the trip id from /trips/<id>?" >&2
        exit 1
      }
      pull "photo_uploads/$t" "photo_uploads/$t" "${PHOTO_EXCLUDES[@]}"
    done
  else
    pull photo_uploads photo_uploads "${PHOTO_EXCLUDES[@]}"
  fi
fi

echo
if [ ${#DRY[@]} -gt 0 ]; then
  echo "dry run — nothing was written. Re-run without -n to transfer."
else
  echo "done. Synced into: $DEST"
  [ ${#DEL[@]} -eq 0 ] && echo "(local-only files were kept; pass --delete to mirror PA exactly)"
fi
