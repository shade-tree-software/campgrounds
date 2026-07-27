#!/usr/bin/env bash
# Forced command for the deploy key. Lives on PythonAnywhere; runs THERE.
#
# ~/.ssh/authorized_keys pins this script to the deploy key:
#
#   command="/home/shadetreesoftware/campgrounds/pa-deploy-remote.sh",restrict ssh-ed25519 AAAA… deploy
#
# With command= set, sshd ignores whatever the client asked to run and executes
# this instead, handing the client's request over in $SSH_ORIGINAL_COMMAND. So
# the key cannot run arbitrary commands: `ssh -i deploy_key pa 'rm -rf ~/photo_uploads'`
# lands here, matches nothing in the case below, and is refused. That is the whole
# point of the key — it can redeploy, and it can do nothing else. `restrict` adds
# no port/agent/X11 forwarding and no PTY.
#
# Keep this allowlist SMALL and keep every branch free of client-supplied data:
# anything interpolated from $SSH_ORIGINAL_COMMAND into a shell command would
# hand back exactly the arbitrary execution the forced command took away.
set -euo pipefail

REPO=/home/shadetreesoftware/campgrounds
# This host also runs the timeline app; only ever reload ekko's worker.
WSGI=/var/www/ekko-shadetreesoftware_pythonanywhere_com_wsgi.py
# Tracked in git AND written by the live admin UI — the files a pull can fight
# with. Reported by `status` so the client can refuse before pulling.
DATA_FILES="campgrounds.json roadside.json"

case "${SSH_ORIGINAL_COMMAND:-deploy}" in
  status)
    # Read-only: fetch and report. Never modifies the working tree.
    cd "$REPO"
    git fetch --quiet
    echo "HEAD=$(git log --oneline -1)"
    echo "COUNT=$(git rev-list --count HEAD..@{u})"
    echo "DIRTY=$(git status --porcelain -- $DATA_FILES | awk '{print $2}' | tr '\n' ' ')"
    echo "TOUCHED=$(git diff --name-only HEAD..@{u} -- $DATA_FILES | tr '\n' ' ')"
    git log --oneline HEAD..@{u} | sed 's/^/INCOMING=/'
    ;;
  reconcile)
    # Called by capture-pa-edits.sh AFTER it has committed and pushed the live
    # UI edits. PA's working copy is then byte-for-byte what the new upstream
    # commit contains, but git still sees the file as locally modified, so the
    # next `git pull` would refuse. Drop the working copy so the pull can land.
    #
    # This is the ONE place that discards live edits, so it is guarded by
    # content: the working file's blob hash must equal the blob in the upstream
    # commit. If they differ by so much as a byte — someone saved another edit
    # in the meantime — it refuses and leaves the file alone, and the next
    # capture picks the edit up. So it can only ever discard data that is
    # already committed and pushed.
    cd "$REPO"
    git fetch --quiet
    for f in $DATA_FILES; do
      git diff --quiet -- "$f" && continue
      live="$(git hash-object "$f")"
      want="$(git rev-parse "@{u}:$f" 2>/dev/null || echo none)"
      if [ "$live" = "$want" ]; then
        git checkout -- "$f"
        echo "reconciled: $f (byte-identical to the pushed commit)"
      else
        echo "SKIPPED: $f differs from the pushed commit — left untouched" >&2
      fi
    done
    ;;
  deploy|deploy-no-reload)
    cd "$REPO"
    # --ff-only so a diverged or conflicting live tree fails loudly rather than
    # merging on the host nobody watches.
    git pull --ff-only
    if [ "${SSH_ORIGINAL_COMMAND:-deploy}" = "deploy" ]; then
      touch "$WSGI"
    fi
    git log --oneline -1
    ;;
  *)
    echo "refused: this key may only run 'status', 'reconcile', 'deploy' or 'deploy-no-reload'" >&2
    exit 2
    ;;
esac
