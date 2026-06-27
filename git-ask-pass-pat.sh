#!/usr/bin/env bash
# ~/git-ask-pass-pat.sh
# Called by Git when it needs a password (or token).

# The token lives in GITHUB_PAT. If it isn't already in the environment, load
# it from the .env file sitting beside this script (the repo's gitignored
# .env), so `git push` works without anyone sourcing .env first.
if [[ -z "$GITHUB_PAT" ]]; then
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$script_dir/.env" ]]; then
        set -a
        # shellcheck disable=SC1091
        source "$script_dir/.env"
        set +a
    fi
fi

# Still missing? Abort with a clear message.
if [[ -z "$GITHUB_PAT" ]]; then
    echo "error: GITHUB_PAT not set and not found in .env beside this script" >&2
    exit 1
fi

# Print the token *only* (no extra whitespace, no newline suppression)
printf '%s' "$GITHUB_PAT"
