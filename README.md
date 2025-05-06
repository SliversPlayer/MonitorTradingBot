# 🧠 MonitorTradingBot

**MonitorTradingBot** es un bot de monitoreo en tiempo real para trading algorítmico, diseñado para evaluar condiciones técnicas sobre criptomonedas (como ADA/USDT) usando datos de Binance. Incluye análisis de contexto de mercado, alertas condicionales, e integración con WhatsApp mediante CallMeBot.

## 🚀 Características

- ✅ Evaluación automática de condiciones técnicas (MACD, RSI, Stoch RSI, EMAs, Volumen)
- 🧭 Clasificación del estado del mercado: `BULLISH`, `BEARISH`, `LATERAL`, `TRANSITION`
- 🔔 Alertas configurables por WhatsApp y/o sonido local
- 📉 Seguimiento activo de operaciones abiertas con cálculo de riesgo/beneficio
- 📊 Análisis técnico en temporalidad configurable (por defecto: 15 minutos)
- 🔒 Arquitectura modular y fácilmente extensible

## 📂 Estructura del proyecto
MonitorTradingBot/
│
├── main.py # Script principal del bot
├── config.py # Parámetros globales (símbolo, temporalidad, etc.)
├── data.py # Descarga y formateo de datos OHLCV
├── indicators.py # Cálculo de indicadores técnicos
├── analysis.py # Evaluación de condiciones y checklist de entrada
├── exchange.py # Conexión con exchange (ccxt)
├── utils.py # Utilidades (sonidos, carga de archivos)
├── callmebot.py # Envío de mensajes vía WhatsApp
│
├── monitor_config.txt # Configuración del bot (alertas)
├── callmebot_credentials.txt# Teléfono y API key CallMeBot (no compartir)
├── entry.txt # Parámetros de la operación activa

## ⚙️ Requisitos

- Python 3.8+
- ccxt
- pandas
- numpy
- ta (Technical Analysis library)
- requests



