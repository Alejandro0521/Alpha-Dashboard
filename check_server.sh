#!/bin/bash
# Check if Alpha Dashboard server is running

PID_FILE="/Users/alejandrobasilio/Desktop/Pruebas Economia /Obtención de Datos Económicos en Tiempo Real (APIs)/Alpha_Dashboard/server.pid"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ALPHA DASHBOARD - SERVER STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check port 8080
if lsof -ti:8080 > /dev/null 2>&1; then
    PID=$(lsof -ti:8080)
    echo "✅ Server is RUNNING"
    echo "   PID: $PID"
    echo "   Port: 8080"
    
    # Get IP
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
    echo ""
    echo "📱 Access from mobile:"
    echo "   http://$LOCAL_IP:8080"
    echo ""
    echo "💻 Access from this Mac:"
    echo "   http://localhost:8080"
else
    echo "❌ Server is NOT running"
    echo ""
    echo "To start: ./start_server_background.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
