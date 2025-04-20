# main.py
"""
Módulo principal del bot de trading
"""
import time
from datetime import datetime
import os
import sys

# Asegurarse de que el script se ejecute desde el directorio correcto
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Importar módulos locales
from config import *
from exchange import get_exchange, validate_symbol
from data import fetch_ohlcv_data
from indicators import calculate_indicators
from analysis import evaluate_checklist
from utils import load_entry_params

def run_bot():
    """Función principal que ejecuta el bot de trading"""
    print(f"Iniciando monitoreo para {SYMBOL} en {EXCHANGE_NAME} con intervalo {INTERVAL}")
    print(f"Verificando condiciones cada {DELAY} segundos...")

    exchange = get_exchange(EXCHANGE_NAME)
    if not exchange:
        print("No se pudo inicializar el exchange. Saliendo...")
        return

    # Validar el símbolo
    if not validate_symbol(exchange, SYMBOL):
        return

    # Configuración para los indicadores
    indicator_config = {
        'SUPERTREND_PERIOD': SUPERTREND_PERIOD,
        'SUPERTREND_MULTIPLIER': SUPERTREND_MULTIPLIER,
        'RSI_PERIOD': RSI_PERIOD,
        'EMA_PERIODS': EMA_PERIODS,
        'VOLUME_SMA_PERIOD': VOLUME_SMA_PERIOD
    }

    while True:
        try:
            entry_params = load_entry_params("entry.txt")
            df = fetch_ohlcv_data(exchange, SYMBOL, INTERVAL, LOOKBACK)
            
            if not df.empty:
                df_ind = calculate_indicators(df, indicator_config)
                evaluate_checklist(df_ind, entry_params)
            else:
                print("No se pudieron obtener datos. Reintentando...")
                
            time.sleep(DELAY)
            
        except Exception as e:
            print(f"Error en el bucle principal: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(DELAY)

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\nBot detenido por el usuario.")
        sys.exit(0)