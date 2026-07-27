---
name: project_deploy_to_pa
description: ./deploy-to-pa.sh ships pushed master to the live PythonAnywhere app (pull + reload) with a data-file guard and a health check
metadata:
  type: project
---

`./deploy-to-pa.sh` (added 2026-07-27) is how code reaches the live site: `git pull` on
PythonAnywhere, then `touch` the ekko WSGI file so the worker restarts. **The reload is not
optional** — PA keeps Python modules and Jinja templates loaded, so a pull alone changes
disk without changing what's served. `-n` dry-runs, `--no-reload` pulls only.

Runs over the restricted deploy key (see [[reference_pa_ssh_keys]]); the actual pull/touch
happens in `pa-deploy-remote.sh` **on PA**, because a forced-command key can't run anything
else. Both files must stay in sync — the wrapper is deployed *by* the deploy it implements,
so a change to it takes one extra deploy to take effect.

**Why not the console API:** it can only type into an already-running console, and consoles
only start when opened in a browser — a deploy built on it breaks silently once the console
is reaped. Scheduled tasks are console-free but have no run-now (daily on free tier).

**Capturing live UI edits: `./capture-pa-edits.sh`** (added 2026-07-27) reads the live
`campgrounds.json`/`roadside.json` down over the read-only sync key, validates, commits,
pushes, then has PA drop its redundant working copy (`reconcile` verb) and deploys. It
refuses when both sides could be right — local uncommitted changes, PA's HEAD not an
ancestor, or a local commit since PA's HEAD that already touched those files (that last is
the silent-loss case: copying down would revert an undeployed sweep commit — deploy first,
then capture). `reconcile` is guarded by blob hash, so it can only discard a working copy
identical to the pushed commit. **Untested against a real edit as of 2026-07-27** — there
were none pending, and the sync key deliberately can't create one.

**The one real hazard: `campgrounds.json` and `roadside.json` are tracked in git AND written
by the live admin UI.** So PA's working tree is legitimately dirty whenever someone edited a
campground since the last sync, and those edits exist ONLY there. The script aborts before
pulling when live edits collide with incoming commits. **Resolve by bringing the live edits
DOWN** (`git diff` over an interactive login, apply here, push) — never `git checkout --` on
PA, which is the destructive move that looks like the quickest fix.

Health check polls `/login` (login-exempt, so 200 proves Flask booted *and* rendered) for
~36s after the reload. **No auto-rollback on failure** — `git reset --hard` would also
destroy uncommitted live campground edits, a worse cure than the disease; it prints the
rollback command instead.

Also warns when local commits aren't pushed: the deploy pulls from GitHub, so unpushed work
silently won't ship.
