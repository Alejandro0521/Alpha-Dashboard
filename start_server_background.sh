#!/bin/bash
# Alpha Dashboard - Permanent Background Server
# Runs in background, survives terminal closure

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/Web"

PORT=8080
LOG_FILE="$DIR/logs/server.log"

# Create logs directory if it doesn't exist
mkdir -p "$DIR/logs"

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo "Starting Alpha Dashboard Server..."
echo "Access from: http://$LOCAL_IP:$PORT"
echo "Logs: $LOG_FILE"

# Start server in background with nohup
nohup python3 -m http.server $PORT > "$LOG_FILE" 2>&1 &

# Save PID
echo $! > "$DIR/server.pid"

echo "✅ Server started (PID: $!)"
echo "To stop: ./stop_server.sh"
