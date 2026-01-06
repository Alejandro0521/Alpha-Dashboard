# 📱 Acceso al Dashboard desde Celular

## 🚀 Inicio Rápido

### 1. Inicia el servidor en tu Mac

Abre Terminal y ejecuta:

```bash
cd "/Users/alejandrobasilio/Desktop/Pruebas Economia /Obtención de Datos Económicos en Tiempo Real (APIs)/Alpha_Dashboard"
./start_server.sh
```

### 2. Conéctate desde tu celular

**IMPORTANTE:** Tu celular debe estar en la **misma red WiFi** que tu Mac.

**Abre el navegador en tu celular y ve a:**

```
http://192.168.1.16:8080
```

**O escanea este código QR:**
_(Puedes generar un QR de esta URL en: https://www.qr-code-generator.com/)_

---

## 🔗 URLs de Acceso

| Dispositivo | URL |
|-------------|-----|
| **📱 Celular/Tablet** | `http://192.168.1.16:8080` |
| **💻 Esta Mac** | `http://localhost:8080` |
| **🖥️ Otra computadora en la red** | `http://192.168.1.16:8080` |

---

## ⚠️ Importante

### Mientras usas el dashboard:
- ✅ Mantén la Terminal abierta (el servidor debe estar corriendo)
- ✅ No cierres la ventana que dice "Servidor iniciado"
- ✅ Tu Mac y celular deben estar en la misma WiFi

### Para detener el servidor:
- Presiona `Ctrl + C` en la Terminal

### Para iniciar de nuevo:
```bash
./start_server.sh
```

---

## 🔧 Solución de Problemas

### ❌ "No se puede conectar" desde el celular

**Verifica que:**
1. **Misma WiFi**: Mac y celular en la misma red
2. **Servidor corriendo**: La Terminal debe mostrar "Servidor iniciado"
3. **IP correcta**: Si tu IP cambió, ejecuta:
   ```bash
   ipconfig getifaddr en0
   ```
   Y usa la nueva IP

### ❌ El firewall bloquea la conexión

En macOS:
1. System Preferences → Security & Privacy → Firewall
2. Firewall Options → Permitir Python

---

## 📲 Acceso Permanente (Opcional)

Si quieres que el servidor inicie automáticamente al encender tu Mac:

```bash
# Agregar a cron
crontab -e
```

Agregar:
```bash
@reboot cd "/Users/alejandrobasilio/Desktop/Pruebas Economia /Obtención de Datos Económicos en Tiempo Real (APIs)/Alpha_Dashboard" && ./start_server.sh &
```

---

## 🌐 Acceso desde Internet (Avanzado)

Si quieres acceder desde cualquier lugar (no solo tu WiFi):

1. **Opción 1:** Usar ngrok (gratis)
   ```bash
   brew install ngrok
   ngrok http 8080
   ```
   Te dará una URL pública temporal

2. **Opción 2:** Configurar port forwarding en tu router
   - Abrir puerto 8080
   - Usar tu IP pública

---

**¡Listo! Ahora puedes ver tu dashboard económico desde cualquier dispositivo en tu red WiFi** 📊📱
