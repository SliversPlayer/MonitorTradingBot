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

📈 Lógica de Señales
El bot evalúa una lista de condiciones como:

Precio sobre EMA9 y EMA20

MACD > Señal

RSI creciente debajo de 60

%K del Stoch RSI cruza 20 al alza

Volumen de compra dominante creciente

Estado de mercado favorable (bullish o transición)

Las señales pueden ser:

✅ Señal COMPLETA: se cumplen casi todas las condiciones

⚠️ Señal PARCIAL: se cumplen al menos 3 condiciones relevantes

❕ Sin señal suficiente: no se cumplen las condiciones mínimas

🛡️ Seguridad
⚠️ No compartas callmebot_credentials.txt en entornos públicos. Este archivo contiene tu número y API key de CallMeBot.

🤖 Créditos
Desarrollado por SliversPlayer. Proyecto educativo y experimental de monitoreo algorítmico para traders independientes.
