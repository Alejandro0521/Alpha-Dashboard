#!/bin/bash
# Alpha Dashboard - Stop Background Server

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$DIR/server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping server (PID: $PID)..."
        kill $PID
        rm "$PID_FILE"
        echo "✅ Server stopped"
    else
        echo "Server not running (PID file exists but process not found)"
        rm "$PID_FILE"
    fi
else
    # Try to find and kill python http.server on port 8080
    PID=$(lsof -ti:8080)
    if [ ! -z "$PID" ]; then
        echo "Found server on port 8080 (PID: $PID)"
        kill $PID
        echo "✅ Server stopped"
    else
        echo "No server running on port 8080"
    fi
fi
