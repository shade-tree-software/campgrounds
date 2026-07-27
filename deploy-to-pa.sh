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
# Guardrails, in the order they fire:
#   - warns when this machine has commits GitHub hasn't got (they can't ship)
#   - aborts when uncommitted live edits to campgrounds.json / roadside.json
#     collide with the incoming commits (those edits exist only on PA)
#   - pulls --ff-only, so a diverged live tree fails instead of merging
#   - after the reload, polls the site and fails loudly if it isn't serving
#
# Usage:
#   ./deploy-to-pa.sh              # pull + reload + health check
#   ./deploy-to-pa.sh -n           # dry run: report what WOULD be pulled
#   ./deploy-to-pa.sh --no-reload  # pull only, leave the running app alone
set -euo pipefail

PA_HOST=shadetreesoftware@ssh.pythonanywhere.com
PA_ROOT=/home/shadetreesoftware/campgrounds
# NB: this host runs two web apps (ekko + timeline). Reload the ekko one only —
# touching the wrong WSGI file restarts an app this deploy didn't change.
PA_WSGI=/var/www/ekko-shadetreesoftware_pythonanywhere_com_wsgi.py
# Login-exempt, so a 200 proves Flask booted and rendered a template without
# needing a session. Anything behind auth would 302 and prove less.
HEALTH_URL=https://ekko-shadetreesoftware.pythonanywhere.com/login
# Tracked in git AND written by the live app — the one place a pull and the
# running site can fight over the same file. See the data-file guard below.
DATA_FILES="campgrounds.json roadside.json"

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

# One round trip that reports everything the guard below needs to decide.
# Emits KEY=value lines: HEAD, DIRTY, TOUCHED, COUNT, INCOMING.
remote_state() {
  pa_ssh "cd '$PA_ROOT' && git fetch --quiet && \
          echo \"HEAD=\$(git log --oneline -1)\" && \
          echo \"COUNT=\$(git rev-list --count HEAD..@{u})\" && \
          echo \"DIRTY=\$(git status --porcelain -- $DATA_FILES | awk '{print \$2}' | tr '\n' ' ')\" && \
          echo \"TOUCHED=\$(git diff --name-only HEAD..@{u} -- $DATA_FILES | tr '\n' ' ')\" && \
          git log --oneline HEAD..@{u} | sed 's/^/INCOMING=/'"
}

state="$(remote_state)"
pa_head="$(sed -n 's/^HEAD=//p' <<<"$state")"
pa_count="$(sed -n 's/^COUNT=//p' <<<"$state")"
pa_dirty="$(sed -n 's/^DIRTY=//p' <<<"$state" | xargs || true)"
pa_touched="$(sed -n 's/^TOUCHED=//p' <<<"$state" | xargs || true)"

echo "live:     $pa_head"
if [ "${pa_count:-0}" -eq 0 ]; then
  echo "incoming: nothing — PA is already up to date"
else
  echo "incoming: $pa_count commit(s)"
  sed -n 's/^INCOMING=/  /p' <<<"$state"
fi

# ── Data-file guard ───────────────────────────────────────────────────────────
# campgrounds.json and roadside.json are tracked in git AND written by the live
# app (campground + roadside admin CRUD). So the live working tree is legitimately
# dirty whenever someone has edited a campground since the last sync, and those
# edits exist ONLY on PA — there is no other copy.
#
# git already refuses to clobber them (the pull would abort), but it does so with
# a wall of git output mid-deploy. Name the collision up front instead, and say
# what the resolution is: bring the live edits DOWN. Never resolve this with
# `git checkout --` on PA, which is exactly the destructive move that looks like
# the quickest fix.
if [ -n "$pa_dirty" ]; then
  if [ -n "$pa_touched" ]; then
    echo "" >&2
    echo "ABORT: uncommitted live edits to [$pa_dirty] and the incoming commits" >&2
    echo "       also change [$pa_touched]. The pull would be refused." >&2
    echo "" >&2
    echo "       Those edits exist only on PA. Bring them down first:" >&2
    echo "         ssh $PA_HOST \"cd $PA_ROOT && git diff -- $pa_dirty\" > /tmp/pa-edits.patch" >&2
    echo "       then apply/commit them here and push. Do NOT 'git checkout --' on PA." >&2
    exit 1
  fi
  echo "note:     live edits to [$pa_dirty] (not touched by the incoming commits — they'll survive)"
fi

if [ "$DRY" -eq 1 ]; then
  echo "== dry run: nothing changed =="
  exit 0
fi

if [ "${pa_count:-0}" -eq 0 ] && [ "$RELOAD" -eq 1 ]; then
  echo "note:     nothing to pull; reloading anyway to pick up any manual changes"
fi

# --ff-only so a dirty or diverged tree on PA fails loudly instead of silently
# creating a merge commit on the live host that nobody will ever see again.
echo "== pulling on PA =="
pa_ssh "cd '$PA_ROOT' && git pull --ff-only"

if [ "$RELOAD" -eq 1 ]; then
  echo "== reloading the web app =="
  pa_ssh "touch '$PA_WSGI'"

  # ── Health check ────────────────────────────────────────────────────────────
  # A reload that boots a broken commit leaves the site 500ing, and without this
  # the deploy would report success and nobody would know until a relative
  # opened the app. /login is login-exempt, so a 200 means Flask started and can
  # render a template — the two things a bad deploy breaks.
  #
  # Deliberately does NOT auto-roll-back: `git reset --hard` would also destroy
  # any uncommitted live campground edits (see the guard above). A loud failure
  # and a human decision is the safer cure.
  echo "== health check =="
  ok=0
  for _ in $(seq 1 12); do
    sleep 3
    code="$(curl -s -o /dev/null -m 15 -w '%{http_code}' "$HEALTH_URL" || echo 000)"
    if [ "$code" = "200" ]; then echo "healthy: HTTP $code"; ok=1; break; fi
    echo "  waiting… (HTTP $code)"
  done
  if [ "$ok" -eq 0 ]; then
    echo "" >&2
    echo "FAILED: $HEALTH_URL did not return 200 after the reload." >&2
    echo "        The site may be down. Previous live commit was:" >&2
    echo "          $pa_head" >&2
    echo "        Check the error log on the PA Web tab, or roll back with:" >&2
    echo "          ssh $PA_HOST \"cd $PA_ROOT && git reset --hard ${pa_head%% *} && touch $PA_WSGI\"" >&2
    echo "        (that discards uncommitted live edits — check 'git status' there first)" >&2
    exit 1
  fi
fi

echo "== live commit =="
pa_ssh "cd '$PA_ROOT' && git log --oneline -1"
