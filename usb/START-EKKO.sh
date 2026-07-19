#!/usr/bin/env bash
#
# START-EKKO.sh — launch the EKKO Trips app straight off this USB stick.
#
# Works fully offline: uses the portable Python bundled under ./python and the
# app source under ./app. Opens the app in your browser automatically.
#
#   Usage:  ./START-EKKO.sh            (then Ctrl+C to stop the server)
#           EKKO_PORT=5050 ./START-EKKO.sh
#           ./START-EKKO.sh --online   (use online OSM/Esri tiles; needs internet)
#
# By default the app serves map tiles from the stick's local store (offline).
# --online forces the online tile CDNs instead, which cover the whole world at
# every zoom (the local store only covers your trip corridor). Useful when you
# have internet and want to pan/zoom into areas the stick doesn't carry.
#
set -euo pipefail

ONLINE_TILES=0
for arg in "$@"; do
  case "$arg" in
    --online) ONLINE_TILES=1 ;;
    *) echo "Unknown option: $arg" >&2; echo "Usage: ./START-EKKO.sh [--online]" >&2; exit 2 ;;
  esac
done

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

# Serve map tiles from the stick when a local tile store is present (offline
# maps). The app also gates on tiles/ existing, so this is safe even before the
# store is built — it just falls back to the online CDNs when online.
# --online skips this so the app uses the online OSM/Esri CDNs instead.
if [ "$ONLINE_TILES" -eq 1 ]; then
  echo " (--online: using online map tiles — needs internet)"
elif [ -d "$APP/tiles" ]; then
  export EKKO_LOCAL_TILES=1
fi

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
