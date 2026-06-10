#!/usr/bin/env bash
# ~/git-ask-pass-pat.sh
# Called by Git when it needs a password (or token).

# The token *must* be in the environment variable GITHUB_PAT.
# If it's missing, we abort with a clear message.
if [[ -z "$GITHUB_PAT" ]]; then
    echo "error: GITHUB_PAT not set – load ~/.github.env first!" >&2
    exit 1
fi

# Print the token *only* (no extra whitespace, no newline suppression)
printf '%s' "$GITHUB_PAT"
