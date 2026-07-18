#!/usr/bin/env bash
#
# START-EKKO.sh — launch the EKKO Trips app straight off this USB stick.
#
# Works fully offline: uses the portable Python bundled under ./python and the
# app source under ./app. Opens the app in your browser automatically.
#
#   Usage:  ./START-EKKO.sh            (then Ctrl+C to stop the server)
#           EKKO_PORT=5050 ./START-EKKO.sh
#
set -euo pipefail

HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PY="$HERE/python/bin/python3"
APP="$HERE/app"
PORT="${EKKO_PORT:-5001}"
URL="http://localhost:$PORT"

if [ ! -x "$PY" ]; then
  echo "ERROR: portable Python not found at:" >&2
  echo "  $PY" >&2
  echo "Plug the stick into a machine WITH internet and run ./build-env.sh first." >&2
  exit 1
fi
if [ ! -f "$APP/ekko_trips_app.py" ]; then
  echo "ERROR: app source not found under $APP" >&2
  exit 1
fi

cd "$APP"

# Load secrets/config (FLASK_SECRET_KEY, TIMELINE_*, RIDB_API_KEY, GITHUB_PAT).
# The app reads these from the environment (it does not auto-load .env), so we
# source it here. Absent .env just means the API-backed extras stay inert.
if [ -f "$APP/.env" ]; then
  set -a; . "$APP/.env"; set +a
fi

# Open the browser once the server is actually listening (backgrounded so the
# server can run in the foreground of this shell).
(
  for _ in $(seq 1 120); do
    if (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; then
      exec 3>&- 3<&- 2>/dev/null || true
      break
    fi
    sleep 0.5
  done
  xdg-open "$URL" >/dev/null 2>&1 || true
) &

echo "==================================================================="
echo " EKKO Trips is starting..."
echo " Open in your browser:  $URL"
echo " Press Ctrl+C in this window to stop the server."
echo "==================================================================="

# --http: plain HTTP is fine on localhost (browsers treat localhost as a secure
# context, so geolocation etc. still work) and avoids self-signed-cert warnings.
exec "$PY" ekko_trips_app.py --http --port "$PORT"
