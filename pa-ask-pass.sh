#!/usr/bin/env bash
# Askpass helper for SSH/rsync against PythonAnywhere, mirroring the existing
# git-ask-pass-pat.sh convention. OpenSSH calls this when it wants a password;
# with SSH_ASKPASS_REQUIRE=force it is used even when a TTY is available, so
# sync-from-pa.sh needs no `sshpass` (which would need a sudo install).
#
# The password lives in PA_PW. If it isn't already exported, load it from the
# gitignored .env beside this script.
if [[ -z "$PA_PW" ]]; then
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$script_dir/.env" ]]; then
        set -a
        # shellcheck disable=SC1091
        source "$script_dir/.env"
        set +a
    fi
fi

if [[ -z "$PA_PW" ]]; then
    echo "error: PA_PW not set and not found in .env beside this script" >&2
    exit 1
fi

printf '%s' "$PA_PW"
