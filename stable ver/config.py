# config.py
"""
Archivo de configuración para el bot de trading
"""
# Configuración
SYMBOL = "ADA/USDT"
INTERVAL = "15m"
LOOKBACK = 100
DELAY = 60
EXCHANGE_NAME = "binance"

# Parámetros de los indicadores
SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3
RSI_PERIOD = 14
EMA_PERIODS = [9, 20, 100]
VOLUME_SMA_PERIOD = 20