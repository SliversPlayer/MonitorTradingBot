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
from callmebot import send_callmebot_message
from utils import load_monitor_config

monitor_config = load_monitor_config()

def run_bot():
    """Función principal que ejecuta el bot de trading"""
    start_msg = f"Iniciando monitoreo para {SYMBOL} en {EXCHANGE_NAME} con intervalo {INTERVAL}"
    print(start_msg)
    delay_msg = f"Verificando condiciones cada {DELAY} segundos..."
    print(delay_msg)
    
    # Enviar mensaje de inicio a WhatsApp
    start_whatsapp_msg = f"🤖 Bot de Trading Iniciado\n{start_msg}\n{delay_msg}\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    if monitor_config.get("whatsapp_alerts"):
        send_callmebot_message(start_whatsapp_msg)
        
    exchange = get_exchange(EXCHANGE_NAME)
    if not exchange:
        error_msg = "No se pudo inicializar el exchange. Saliendo..."
        print(error_msg)
        if monitor_config.get("whatsapp_alerts"):
            send_callmebot_message(f"❌ ERROR: {error_msg}")
        return

    # Validar el símbolo
    if not validate_symbol(exchange, SYMBOL):
        error_msg = f"El símbolo {SYMBOL} no está disponible en {EXCHANGE_NAME}"
        print(error_msg)
        send_callmebot_message(f"❌ ERROR: {error_msg}")
        return

    # Configuración para los indicadores
    indicator_config = {
        'SUPERTREND_PERIOD': SUPERTREND_PERIOD,
        'SUPERTREND_MULTIPLIER': SUPERTREND_MULTIPLIER,
        'RSI_PERIOD': RSI_PERIOD,
        'EMA_PERIODS': EMA_PERIODS,
        'VOLUME_SMA_PERIOD': VOLUME_SMA_PERIOD,
        'INTERVAL': INTERVAL  # Añadido para poder ajustar umbrales por temporalidad
    }

    while True:
        try:
            entry_params = load_entry_params("entry.txt")
            df = fetch_ohlcv_data(exchange, SYMBOL, INTERVAL, LOOKBACK)
            
            if not df.empty:
                df_ind = calculate_indicators(df, indicator_config)
                evaluate_checklist(df_ind, entry_params)
            else:
                error_msg = "No se pudieron obtener datos. Reintentando..."
                print(error_msg)
                send_callmebot_message(f"⚠️ {error_msg}")
                
            time.sleep(DELAY)
            
        except Exception as e:
            error_msg = f"Error en el bucle principal: {e}"
            print(error_msg)
            # Enviamos el error a WhatsApp
            send_callmebot_message(f"⚠️ ERROR en Bot de Trading: {error_msg}")
            import traceback
            traceback.print_exc()
            time.sleep(DELAY)


if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        exit_msg = "\nBot detenido por el usuario."
        print(exit_msg)
        send_callmebot_message("🛑 Bot de Trading detenido manualmente.")
        sys.exit(0)