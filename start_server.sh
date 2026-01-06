#!/bin/bash
# Alpha Dashboard - Web Server Launcher
# Starts HTTP server for mobile/remote access

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           ALPHA DASHBOARD - WEB SERVER                    ║"
echo "║          Access from Phone/Tablet/Other Devices           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/Web"

# Get local IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
else
    # Linux
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

if [ -z "$LOCAL_IP" ]; then
    echo "⚠️  No se pudo detectar la IP local automáticamente"
    echo "Intenta ejecutar: ifconfig | grep 'inet '"
    LOCAL_IP="tu-ip-local"
fi

PORT=8080

echo "🌐 Iniciando servidor web..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 ACCESO DESDE DISPOSITIVOS MÓVILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  En tu CELULAR, conéctate a la misma red WiFi que tu Mac"
echo ""
echo "2️⃣  Abre el navegador en tu celular y ve a:"
echo ""
echo "    🔗 http://$LOCAL_IP:$PORT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💻 Desde esta computadora:"
echo "    🔗 http://localhost:$PORT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANTE: Mantén esta ventana abierta mientras usas el dashboard"
echo "    Para detener el servidor, presiona Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Servidor iniciado en el puerto $PORT..."
echo ""

# Start Python HTTP server
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer $PORT
else
    echo "❌ Error: Python no encontrado"
    exit 1
fi
