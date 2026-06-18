#!/usr/bin/env sh
# Wire this project's git-tracked memory into Claude Code's auto-memory.
#
# Why this exists: Claude Code stores auto-memory per-project under
# ~/.claude/projects/<encoded-path>/memory and never commits it, so it does NOT
# travel with the repo. We instead keep the memory files in-repo at
# .claude/memory/ (versioned, travels with clone/pull) and point Claude at them
# via the `autoMemoryDirectory` setting. But that setting only accepts an
# absolute or ~/ path (no repo-relative / $VAR expansion), so a single committed
# value can't follow the repo to an arbitrary clone path. This script (run from a
# committed SessionStart hook, which receives $CLAUDE_PROJECT_DIR) bridges the
# gap: it makes the fixed ~/ path that `autoMemoryDirectory` names a symlink to
# the in-repo memory dir, wherever the repo happens to live. Result: a fresh
# clone + start Claude needs zero manual setup (beyond the one-time folder-trust
# accept), and memories Claude writes land in the repo, ready to commit.
#
# Idempotent: safe to run on every session start.
set -u

# Project root: prefer the hook-provided var; fall back to this script's location.
PROJ="${CLAUDE_PROJECT_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
TARGET="$PROJ/.claude/memory"
# LINK must exactly match `autoMemoryDirectory` in .claude/settings.json.
LINK="$HOME/.claude/memory-links/ekko-campgrounds"

mkdir -p "$TARGET" "$(dirname "$LINK")" 2>/dev/null || true

changed=0
if [ "$(readlink "$LINK" 2>/dev/null || true)" != "$TARGET" ]; then
  changed=1
  # If a real (non-symlink) path already sits at LINK -- e.g. Claude created a
  # memory dir there before this hook first ran -- preserve anything written into
  # the repo (no-clobber, repo copy wins) and then replace it with the symlink.
  if [ -e "$LINK" ] && [ ! -L "$LINK" ]; then
    if [ -d "$LINK" ]; then
      cp -an "$LINK"/. "$TARGET"/ 2>/dev/null || cp -rn "$LINK"/. "$TARGET"/ 2>/dev/null || true
      rm -rf "$LINK"
    else
      rm -f "$LINK"
    fi
  fi
  ln -nsf "$TARGET" "$LINK"
fi

# Recall insurance: the SessionStart hook may run after auto-memory has already
# been loaded for this session, so on the wiring event (first run on a machine, or
# the repo moved) surface the index via stdout -- SessionStart stdout is added to
# the session context. Steady state stays silent to avoid duplicating the index.
if [ "$changed" = 1 ] && [ -f "$TARGET/MEMORY.md" ]; then
  printf '%s\n' "<project-memory note=\"wired $LINK -> $TARGET; index follows\">"
  cat "$TARGET/MEMORY.md"
  printf '%s\n' "</project-memory>"
fi
exit 0
