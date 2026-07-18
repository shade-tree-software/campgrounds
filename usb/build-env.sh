#!/usr/bin/env bash
#
# build-env.sh — (re)build the portable Python environment on this stick.
#
# REQUIRES INTERNET. Run this once on any internet-connected x86_64 Linux
# machine to populate ./python with a self-contained CPython + all the app's
# dependencies. After that the stick runs fully offline via START-EKKO.sh.
#
# Safe to re-run: it reinstalls/updates dependencies. Pass --fresh to also
# re-download the Python interpreter from scratch.
#
set -euo pipefail

HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PY_DIR="$HERE/python"
REQ="$HERE/requirements-ekko.txt"

# Pinned python-build-standalone release: a fully self-contained, relocatable
# CPython 3.12 for x86_64 Linux (glibc). Runs on any reasonably recent distro
# without needing system Python or dev libraries.
PBS_TAG="20250612"
PBS_FILE="cpython-3.12.11+20250612-x86_64-unknown-linux-gnu-install_only.tar.gz"
PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PBS_TAG}/${PBS_FILE}"

FRESH=0
[ "${1:-}" = "--fresh" ] && FRESH=1

if [ "$FRESH" = "1" ]; then
  rm -rf "$PY_DIR"
fi

if [ ! -x "$PY_DIR/bin/python3" ]; then
  echo ">> Downloading portable Python ($PBS_FILE)..."
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  curl -L --fail --retry 3 -o "$tmp/py.tar.gz" "$PBS_URL"
  echo ">> Extracting..."
  tar -xzf "$tmp/py.tar.gz" -C "$tmp"        # extracts to $tmp/python
  rm -rf "$PY_DIR"
  mv "$tmp/python" "$PY_DIR"
  echo ">> Portable Python installed at $PY_DIR"
fi

echo ">> Upgrading pip..."
"$PY_DIR/bin/python3" -m pip install --upgrade pip

echo ">> Installing app dependencies from $REQ ..."
"$PY_DIR/bin/python3" -m pip install -r "$REQ"

echo ">> Verifying key imports..."
"$PY_DIR/bin/python3" - <<'PYEOF'
import importlib
mods = ["flask", "flask_login", "werkzeug", "jinja2", "PIL", "geopy",
        "requests", "dotenv", "timezonefinder", "numpy", "cryptography", "OpenSSL"]
missing = []
for m in mods:
    try:
        importlib.import_module(m)
    except Exception as e:
        missing.append(f"{m}: {e}")
if missing:
    print("MISSING/BROKEN:")
    for x in missing:
        print("  -", x)
    raise SystemExit(1)
print("All key imports OK.")
PYEOF

echo ">> Done. The stick is ready to run offline via ./START-EKKO.sh"
