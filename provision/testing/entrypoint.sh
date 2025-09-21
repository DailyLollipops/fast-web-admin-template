#!/bin/bash
set -e

/usr/bin/supervisord -c /etc/supervisord.conf >/dev/null 2>&1 &
SUP_PID=$!
echo "Supervisor started (pid $SUP_PID)"
echo "Waiting for supervisor processes"
# Sleep for now
sleep 10
echo "Done waiting"

# Run the actual command
exec "$@"
