#!/bin/bash
set -e

/usr/bin/supervisord -c /etc/supervisord.conf >/dev/null 2>&1 &
SUP_PID=$!

echo "Supervisor started (pid $SUP_PID)"

# Run the actual command
exec "$@"
