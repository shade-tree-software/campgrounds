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
    echo "refused: this key may only run 'status', 'deploy' or 'deploy-no-reload'" >&2
    exit 2
    ;;
esac
