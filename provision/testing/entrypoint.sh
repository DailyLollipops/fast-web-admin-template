#!/bin/bash
set -e

/usr/bin/supervisord -c /etc/supervisord.conf >/dev/null 2>&1 &
SUP_PID=$!

echo "Supervisor started (pid $SUP_PID)"
echo "Waiting for ports 8000 to be available..."
echo "Waiting for ports 5173 to be available..."

wait_for_port () {
  local port=$1
  while ! lsof -iTCP:${port} -sTCP:LISTEN >/dev/null 2>&1; do
    echo "  → waiting for port ${port}..."
    sleep 1
  done
  echo "  ✓ port ${port} is listening"
}

wait_for_port 8000
wait_for_port 5173

echo "All ports are up. Continuing."

echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &

echo "Starting window manager..."
fluxbox &

echo "Starting x11vnc..."
x11vnc -display :99 \
  -forever \
  -nopw \
  -listen 0.0.0.0 \
  -xkb &

echo "Starting noVNC..."
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &

# Run the actual command
exec "$@"
