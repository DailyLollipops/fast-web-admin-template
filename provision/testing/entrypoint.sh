#!/bin/bash
set -e

/usr/bin/supervisord -c /etc/supervisord.conf >/dev/null 2>&1 &
SUP_PID=$!

echo "Supervisor started (pid $SUP_PID)"
echo "Waiting for ports 8000 to be available..."

wait_for_port () {
  local port=$1
  while ! lsof -iTCP:${port} -sTCP:LISTEN >/dev/null 2>&1; do
    echo "  → waiting for port ${port}..."
    sleep 1
  done
  echo "  ✓ port ${port} is listening"
}

wait_for_port 8000

echo "All ports are up. Continuing."

# Run the actual command
exec "$@"
