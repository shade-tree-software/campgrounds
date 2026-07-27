#!/usr/bin/env bash
# Deploy the pushed master to the live PythonAnywhere app: git pull, then
# reload the web app so the running worker picks up the new code.
#
# Why SSH rather than the API or a console: PythonAnywhere's console API can
# only "type" into a console that is ALREADY RUNNING, and a console only starts
# when someone opens it in a browser — so a deploy built on it breaks silently
# whenever that console gets reaped. SSH (a paid-plan feature) starts a fresh
# shell per invocation and returns a real exit status, so a failed pull fails
# the script instead of vanishing into a terminal nobody is watching.
#
# Auth: your PythonAnywhere password in PA_PW (gitignored .env), fed to ssh via
# pa-ask-pass.sh — the same mechanism sync-from-pa.sh uses. No sshpass, no sudo,
# and the password never appears in the process list or in this script's output.
#
# The reload is NOT optional: PythonAnywhere keeps your Python modules and
# Jinja templates loaded in the worker, so a pull alone changes the files on
# disk without changing what the site serves. Touching the WSGI file is how you
# ask PA to restart that worker.
#
# Usage:
#   ./deploy-to-pa.sh              # pull + reload
#   ./deploy-to-pa.sh -n           # dry run: report what WOULD be pulled
#   ./deploy-to-pa.sh --no-reload  # pull only, leave the running app alone
set -euo pipefail

PA_HOST=shadetreesoftware@ssh.pythonanywhere.com
PA_ROOT=/home/shadetreesoftware/campgrounds
# NB: this host runs two web apps (ekko + timeline). Reload the ekko one only —
# touching the wrong WSGI file restarts an app this deploy didn't change.
PA_WSGI=/var/www/ekko-shadetreesoftware_pythonanywhere_com_wsgi.py

HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DRY=0
RELOAD=1

while [ $# -gt 0 ]; do
  case "$1" in
    -n|--dry-run)  DRY=1; shift ;;
    --no-reload)   RELOAD=0; shift ;;
    -h|--help)     sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Feed the password to ssh without a TTY prompt. SSH_ASKPASS_REQUIRE=force needs
# OpenSSH 8.4+; setsid detaches from the terminal so ssh actually consults it.
export SSH_ASKPASS="$HERE/pa-ask-pass.sh"
export SSH_ASKPASS_REQUIRE=force
[ -x "$SSH_ASKPASS" ] || { echo "error: $SSH_ASKPASS missing or not executable" >&2; exit 1; }

# accept-new: pin PA's host key on first use, but still fail on a CHANGED key
# (a silent StrictHostKeyChecking=no would accept an impostor).
pa_ssh() {
  setsid ssh -o StrictHostKeyChecking=accept-new \
             -o PreferredAuthentications=password \
             -o PubkeyAuthentication=no \
             "$PA_HOST" "$@"
}

# Warn (don't block) when this machine is ahead of the remote: the deploy pulls
# from GitHub, so anything not pushed simply won't ship, and finding that out
# from a "nothing changed" site is worse than a line of output here.
if git -C "$HERE" rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
  unpushed="$(git -C "$HERE" log --oneline @{u}.. 2>/dev/null | wc -l || echo 0)"
  if [ "$unpushed" -gt 0 ]; then
    echo "warning: $unpushed local commit(s) not pushed — they will NOT be deployed" >&2
  fi
fi

if [ "$DRY" -eq 1 ]; then
  echo "== dry run: fetching on PA, nothing will change =="
  pa_ssh "cd '$PA_ROOT' && git fetch --quiet && \
          echo 'live:    ' \$(git log --oneline -1) && \
          echo 'incoming:' && git log --oneline HEAD..@{u} | sed 's/^/  /' && \
          { [ -n \"\$(git status --porcelain)\" ] && echo 'WARNING: working tree is dirty on PA'; true; }"
  exit 0
fi

# --ff-only so a dirty or diverged tree on PA fails loudly instead of silently
# creating a merge commit on the live host that nobody will ever see again.
echo "== pulling on PA =="
pa_ssh "cd '$PA_ROOT' && git pull --ff-only"

if [ "$RELOAD" -eq 1 ]; then
  echo "== reloading the web app =="
  pa_ssh "touch '$PA_WSGI'"
fi

echo "== live commit =="
pa_ssh "cd '$PA_ROOT' && git log --oneline -1"
