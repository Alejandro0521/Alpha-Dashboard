# 🤖 Instalación de Actualizaciones Automáticas

## ⚡ Instalación Rápida (Recomendado)

Ejecuta este comando en la terminal:

```bash
cd "/Users/alejandrobasilio/Desktop/Pruebas Economia /Obtención de Datos Económicos en Tiempo Real (APIs)/Alpha_Dashboard"
./install_cron.sh
```

El script te preguntará si quieres instalar y luego configurará todo automáticamente.

---

## 📅 Calendario de Actualizaciones

Una vez instalado, el sistema se actualizará automáticamente así:

| Tipo de Datos | Frecuencia | Horario | Días |
|---------------|------------|---------|------|
| **Banxico** (TIIE, Cetes, M1, UDI) | 1 vez al día | 11:30 AM | Todos los días |
| **Acciones USA** (AAPL, MSFT, etc.) | Cada hora | 9 AM - 3 PM | Lunes a Viernes |
| **Indicadores Globales** (VIX, S&P, Oro) | Cada hora | 9 AM - 3 PM | Lunes a Viernes |
| **USD/MXN en tiempo real** | Ya automático | Cada 60 seg | Siempre (en página web) |

---

## 📝 Logs

Los logs de cada actualización se guardan en:

```
logs/banxico.log    - Actualizaciones diarias de Banxico
logs/markets.log    - Actualizaciones de mercados cada hora
```

Para ver los logs en tiempo real:

```bash
tail -f logs/banxico.log
tail -f logs/markets.log
```

---

## 🛠️ Comandos Útiles

### Ver cron jobs instalados
```bash
crontab -l
```

### Editar cron jobs manualmente
```bash
crontab -e
```

### Remover cron jobs
```bash
crontab -e
# Eliminar las líneas que dicen "Alpha Dashboard"
```

### Ejecutar actualización manual
```bash
# Actualizar todo
python3 run_pipeline.py

# Solo Banxico
./update_banxico.sh

# Solo mercados
./update_markets.sh
```

---

## ⚠️ Solución de Problemas

### "Permission denied" al ejecutar install_cron.sh

```bash
chmod +x install_cron.sh
./install_cron.sh
```

### Los cron jobs no se ejecutan

1. Verifica que cron tiene permisos en macOS:
   - System Preferences → Security & Privacy → Privacy → Full Disk Access
   - Agregar `/usr/sbin/cron`

2. Verifica la ruta de Python:
```bash
which python3
```

Si no es `/usr/bin/python3`, edita los scripts y cambia la ruta.

### Ver si los scripts se ejecutaron

```bash
ls -ltr logs/
cat logs/banxico.log
cat logs/markets.log
```

---

## 🔄 Desinstalar Actualizaciones Automáticas

```bash
crontab -l > cron_backup.txt  # Backup
crontab -e  # Editar
# Elimina las líneas que digan "Alpha Dashboard"
```

---

## 📊 Verificar que Funciona

Después de instalar, espera a que se ejecute la primera actualización o ejecuta manualmente:

```bash
./update_markets.sh
```

Luego abre `Web/index.html` y verifica que los datos sean recientes.

---

**¿Necesitas ayuda?** Revisa los logs en la carpeta `logs/`
