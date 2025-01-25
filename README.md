# Advanced WiFi Network Scanner 🛜

## 📡 Descripción
wifi_info_basica es una herramienta potente y versátil para el análisis y monitoreo de redes WiFi. Desarrollada en Python, esta aplicación combina una interfaz gráfica moderna con capacidades avanzadas de escaneo de redes inalámbricas.

[WiFi Scanner Demo](screenshot.png)

## 🚀 Características Principales
- ✨ Interfaz gráfica moderna y fácil de usar
- 🔍 Escaneo en tiempo real de redes WiFi
- 📊 Información detallada de cada red:
  - Nombre de la red (SSID)
  - Dirección MAC (BSSID)
  - Intensidad de señal (dBm)
  - Distancia aproximada
  - Tipo de encriptación
  - Canal de frecuencia
  - Frecuencia de operación
- 💾 Exportación de datos a archivos JSON
- 🔐 Capacidad de intentar conexiones a redes
- 📈 Actualizaciones automáticas cada 5 segundos

## 🛠️ Requisitos del Sistema
- Python 3.7 o superior
- Sistema operativo compatible:
  - Windows 10/11
  - Linux (requiere privilegios root)
  - macOS (funcionalidad limitada)

## 📦 Dependencias
```bash
pywifi>=1.19.0
flask>=2.0.0
tkinter
tkinterweb>=3.0.0
