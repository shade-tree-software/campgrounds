---
name: reference_pa_ssh_keys
description: PythonAnywhere SSH is key-only from this machine — two restricted keys (deploy / read-only sync), no account password stored anywhere
metadata:
  type: reference
---

Since 2026-07-27 this machine reaches PythonAnywhere with two **restricted, passphrase-less**
ed25519 keys instead of the account password. `PA_PW` is gone from `.env` and
`pa-ask-pass.sh` is deleted.

`~/.ssh/authorized_keys` **on PA** (installed once over a password login):

```
command="/home/shadetreesoftware/campgrounds/pa-deploy-remote.sh",restrict  ssh-ed25519 … deploy
command="/usr/bin/rrsync -ro /home/shadetreesoftware/campgrounds",restrict  ssh-ed25519 … sync
```

- `~/.ssh/pa_deploy_ed25519` → runs `pa-deploy-remote.sh` (in the repo) and nothing else.
  It accepts exactly `status`, `deploy`, `deploy-no-reload` via `$SSH_ORIGINAL_COMMAND`
  and refuses anything else. Used by `./deploy-to-pa.sh`.
- `~/.ssh/pa_sync_ed25519` → `rrsync -ro`, i.e. read-only under the repo dir. Used by
  `./sync-from-pa.sh`, whose **remote paths are relative to that root** (`$PA_HOST:/trip_data/`).

**Verified on install (re-run these after any change):** an arbitrary command on the deploy
key is refused (exit 2); `status` works; an arbitrary command on the sync key gives
`rrsync error: SSH_ORIGINAL_COMMAND does not run rsync`; an rsync *upload* gives
`sending to read-only server is not allowed`. PA's sshd is stock OpenSSH 8.9 and honors
`command=` — this is NOT documented by PA, so re-test it if they change hosts.

**What this does and does not buy.** A stolen key can only redeploy (or only read) — it
cannot get a shell, delete files, or write. But **password auth is still enabled server-side**
(`publickey,password`) and `sshd_config` isn't ours to edit, so anyone with the PA *account*
password can still log in fully. Guard that password; consider whether PA 2FA covers SSH.

Interactive/admin work (rollbacks, reading live edits) still needs a password login — by
design, so routine automation can't do it. Both scripts pass `BatchMode=yes` +
`PasswordAuthentication=no` so a rejected key fails loudly instead of silently prompting.

Keys are passphrase-less so deploys can run unattended; `ssh-keygen -p -f <key>` adds one
if deploys should require an unlocked agent (i.e. a human present).

Related: [[reference_sync_from_pa]], [[project_deploy_to_pa]].
