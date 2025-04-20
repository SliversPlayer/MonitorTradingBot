# analysis.py
"""
Módulo para analizar datos y generar señales
"""
from datetime import datetime
from utils import alert_signal

def check_trade_status(latest_close, entry_params):
    """Verifica el estado de una operación en curso"""
    try:
        if "entry_price" not in entry_params or not entry_params["entry_price"]:
            print("📌 No se ha definido un precio de entrada en el archivo. No se realizará seguimiento.")
            return

        entry = entry_params["entry_price"]
        current_price = latest_close
        change_pct = ((current_price - entry) / entry) * 100
        result = f"🎯 Seguimiento de operación:\n"
        result += f"   🔹 Precio entrada: {entry:.6f}\n"
        result += f"   🔹 Precio actual : {current_price:.6f} ({change_pct:+.2f}%)\n"

        if "take_profit" in entry_params:
            tp = entry_params["take_profit"]
            pct_to_tp = ((tp - current_price) / current_price) * 100
            result += f"   🟢 A TP ({tp:.6f}): {pct_to_tp:+.2f}%\n"

        if "stop_loss" in entry_params:
            sl = entry_params["stop_loss"]
            pct_to_sl = ((sl - current_price) / current_price) * 100
            result += f"   🔴 A SL ({sl:.6f}): {pct_to_sl:+.2f}%\n"

        if "take_profit" in entry_params and "stop_loss" in entry_params:
            risk = abs(entry - entry_params["stop_loss"])
            reward = abs(entry_params["take_profit"] - entry)
            rr_ratio = reward / risk if risk != 0 else float("inf")
            result += f"   📊 Risk/Reward Ratio: {rr_ratio:.2f}\n"

        print(result)

    except Exception as e:
        print(f"Error en seguimiento de operación: {e}")

def evaluate_checklist(df, entry_params):
    """Evalúa las condiciones de trading basadas en los indicadores"""
    try:
        if len(df) < 3:
            print("No hay suficientes datos para evaluar la lista de verificación")
            return

        latest = df.iloc[-1]
        previous = df.iloc[-2]
        before_previous = df.iloc[-3]

        # Extraer valores
        latest_close = latest["Close"]
        latest_ema9 = latest["EMA9"]
        latest_ema20 = latest["EMA20"]

        latest_macd = latest["MACD"]
        prev_macd = previous["MACD"]
        latest_macd_signal = latest["MACD_Signal"]
        prev_macd_signal = previous["MACD_Signal"]

        latest_rsi = latest["RSI"]
        prev_rsi = previous["RSI"]

        latest_stoch_k = latest["Stoch_K"]
        prev_stoch_k = previous["Stoch_K"]

        latest_volume = latest["Volume"]
        prev_volume = previous["Volume"]
        latest_volume_sma = latest["Volume_SMA"]

        # Supertrend confirmado en vela cerrada (SOLO INFORMATIVO)
        confirmed_st_direction = previous["Supertrend_Direction"]
        confirmed_st_value = previous["Supertrend"]

        supertrend_status = "🟩" if confirmed_st_direction else "🟥"
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] SUPERTREND: {supertrend_status} ({'COMPRA' if confirmed_st_direction else 'VENTA'}) - Valor: {confirmed_st_value:.6f}")

        # Dirección del precio
        price_direction = "⬆️" if latest_close > previous["Close"] else "⬇️"
        macd_direction = "⬆️" if latest_macd > prev_macd else "⬇️"

        # Lista de condiciones activas (SIN Supertrend)
        conditions_with_values = {
            f"Precio sobre EMA9 y EMA20 {price_direction} (Precio: {latest_close:.6f}, EMA9: {latest_ema9:.6f}, EMA20: {latest_ema20:.6f})":
                (latest_close > latest_ema9) and (latest_close > latest_ema20),

            f"MACD > Signal {macd_direction} (MACD: {latest_macd:.6f}, Signal: {latest_macd_signal:.6f}, MACD Anterior: {prev_macd:.6f})":
                latest_macd > latest_macd_signal,

            f"RSI < 60 y subiendo (RSI actual: {latest_rsi:.2f}, RSI anterior: {prev_rsi:.2f})":
                (latest_rsi < 60) and (latest_rsi > prev_rsi),

            f"Stoch RSI %K cruza 20 al alza (K actual: {latest_stoch_k:.2f}, K anterior: {prev_stoch_k:.2f})":
                (prev_stoch_k < 20) and (latest_stoch_k > 20),

            f"Volumen > promedio (Volumen: {latest_volume:.2f}, SMA20: {latest_volume_sma:.2f})":
                latest_volume > latest_volume_sma,

            f"Volumen creciente (Vol actual: {latest_volume:.2f}, Vol anterior: {prev_volume:.2f})":
                latest_volume > prev_volume * 1.1
        }

        # Mostrar info de Supertrend (solo informativo)
        print(f"ℹ️ Supertrend: {'✔️' if confirmed_st_direction else '❌'} "
              f"{'En dirección COMPRA' if confirmed_st_direction else 'En dirección VENTA'} "
              f"(Valor: {confirmed_st_value:.6f})")

        total = len(conditions_with_values)
        ok = sum(conditions_with_values.values())

        print(f"Condiciones cumplidas: {ok}/{total}")
        for k, v in conditions_with_values.items():
            print(f"{'✔️' if v else '❌'} {k}")

        if ok == total:
            print(f"✅ Señal COMPLETA: Todos los criterios cumplidos. Precio actual: {latest_close:.6f}")
            alert_signal("complete")
        elif ok >= 3:
            print(f"⚠️ Señal Parcial: {ok}/{total} criterios cumplidos. Precio actual: {latest_close:.6f}")
            alert_signal("partial")
        else:
            print(f"❌ Sin señal suficiente: Solo {ok}/{total} criterios cumplidos. Precio actual: {latest_close:.6f}")

    except Exception as e:
        print(f"Error al evaluar lista de verificación: {e}")
        import traceback
        traceback.print_exc()

    check_trade_status(latest["Close"], entry_params)