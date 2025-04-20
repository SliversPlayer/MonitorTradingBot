# analysis.py
"""
Módulo para analizar datos y generar señales
"""
from datetime import datetime
from utils import alert_signal
from config import VOLUME_SMA_PERIOD


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
        result += f"   🔹 Precio entrada: {entry:.4f}\n"
        result += f"   🔹 Precio actual : {current_price:.4f} ({change_pct:+.2f}%)\n"

        if "take_profit" in entry_params:
            tp = entry_params["take_profit"]
            pct_to_tp = ((tp - current_price) / current_price) * 100
            result += f"   🟢 A TP ({tp:.4f}): {pct_to_tp:+.2f}%\n"

        if "stop_loss" in entry_params:
            sl = entry_params["stop_loss"]
            pct_to_sl = ((sl - current_price) / current_price) * 100
            result += f"   🔴 A SL ({sl:.4f}): {pct_to_sl:+.2f}%\n"

        if "take_profit" in entry_params and "stop_loss" in entry_params:
            risk = abs(entry - entry_params["stop_loss"])
            reward = abs(entry_params["take_profit"] - entry)
            rr_ratio = reward / risk if risk != 0 else float("inf")
            result += f"   📊 Risk/Reward Ratio: {rr_ratio:.2f}\n"

        print(result)

    except Exception as e:
        print(f"Error en seguimiento de operación: {e}")

def safe_get(series, key, default=0):
    """Obtiene un valor de forma segura de una Series, devolviendo un default si hay error"""
    try:
        return series[key]
    except (KeyError, IndexError, TypeError):
        print(f"⚠️ No se encontró el indicador '{key}'. Usando valor predeterminado.")
        return default

def evaluate_checklist(df, entry_params):
    """Evalúa las condiciones de trading basadas en los indicadores"""
    try:
        if len(df) < 3:
            print("No hay suficientes datos para evaluar la lista de verificación")
            return

        latest = df.iloc[-1]
        previous = df.iloc[-2]
        before_previous = df.iloc[-3]

        # Extraer valores (usando safe_get para evitar KeyError)
        latest_close = latest["Close"]
        latest_ema9 = safe_get(latest, "EMA9", latest_close * 0.95)
        latest_ema20 = safe_get(latest, "EMA20", latest_close * 0.90)

        latest_macd = safe_get(latest, "MACD")
        prev_macd = safe_get(previous, "MACD")
        latest_macd_signal = safe_get(latest, "MACD_Signal")
        prev_macd_signal = safe_get(previous, "MACD_Signal")
        histogram_macd = latest_macd - latest_macd_signal

        latest_rsi = safe_get(latest, "RSI", 50)
        prev_rsi = safe_get(previous, "RSI", 50)

        latest_stoch_k = safe_get(latest, "Stoch_K", 50)
        prev_stoch_k = safe_get(previous, "Stoch_K", 50)

        latest_volume = latest["Volume"]
        prev_volume = previous["Volume"]
        latest_volume_sma = safe_get(latest, "Volume_SMA", latest_volume * 0.9)
        latest_buy_volume = safe_get(previous, "BuyVolume")
        prev_buy_volume = safe_get(before_previous, "BuyVolume")
        buy_volume_sma = safe_get(previous, "BuyVolume_SMA")

        # Volumen comprador y vendedor
        latest_buy_volume = safe_get(latest, "BuyVolume")
        prev_buy_volume = safe_get(previous, "BuyVolume")
        latest_sell_volume = safe_get(latest, "SellVolume")
        prev_sell_volume = safe_get(previous, "SellVolume")
        buy_volume_sma = safe_get(latest, "BuyVolume_SMA")
        
        # Determinar volumen dominante y si es creciente
        if latest_buy_volume >= latest_sell_volume:
            dominant = "COMPRA"
            emoji = "🟢"
            # Solo considerar creciente si el volumen anterior no era cero
            growing = latest_buy_volume > prev_buy_volume * 1.1 and prev_buy_volume > 0
        else:
            dominant = "VENTA"
            emoji = "🔴"
            growing = latest_sell_volume > prev_sell_volume * 1.1 and prev_sell_volume > 0
        
        # Versión simplificada en una sola línea
        vol_type = "COMPRA" if dominant == "COMPRA" else "VENTA"
        vol_current = latest_buy_volume if dominant == "COMPRA" else latest_sell_volume
        vol_prev = prev_buy_volume if dominant == "COMPRA" else prev_sell_volume
        vol_change_emoji = "+" if growing else "-"
        vol_comparison = f"{vol_change_emoji} ({latest_volume:,.0f} vs {prev_volume:,.0f})"
        vol_sma_status = f"↑SMA{VOLUME_SMA_PERIOD}" if latest_volume > buy_volume_sma else f"↓SMA{VOLUME_SMA_PERIOD}"
        
        # Determinar tipo de vela y volumen dominante
        is_green_current = latest["Close"] > latest["Open"]
        is_green_previous = previous["Close"] > previous["Open"]
        
        # Asignar valores correctos según tipo
        actual_vol = latest_buy_volume if is_green_current else safe_get(previous, "SellVolume")
        prev_vol = prev_buy_volume if is_green_previous else safe_get(before_previous, "SellVolume")      
        volumen_ok = is_green_current and is_green_previous and latest_buy_volume > prev_buy_volume * 1.1

        # Supertrend confirmado en vela cerrada (solo informativo)
        confirmed_st_direction = safe_get(previous, "Supertrend_Direction", True)
        confirmed_st_value = safe_get(previous, "Supertrend", latest_close)
        st_diff = latest_close - confirmed_st_value

        # Dirección del precio
        price_direction = "⬆️" if latest_close > previous["Close"] else "⬇️"
        macd_direction = "⬆️" if latest_macd > prev_macd else "⬇️"

        conditions_with_values = {
            f"EMA9 y EMA20 sobre precio {price_direction} (EMA9: {latest_ema9:.4f}, EMA20: {latest_ema20:.4f})":
                (latest_close > latest_ema9) and (latest_close > latest_ema20),
        
            f"MACD > Signal {macd_direction} (MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}, Histo: {histogram_macd:.4f})":
                latest_macd > latest_macd_signal,
        
            f"RSI < 60 y subiendo (RSI actual: {latest_rsi:.2f}, RSI Prev: {prev_rsi:.2f})":
                (latest_rsi < 60) and (latest_rsi > prev_rsi),
        
            f"Stoch RSI %K cruza 20 al alza (K actual: {latest_stoch_k:.2f}, K Prev: {prev_stoch_k:.2f})":
                (prev_stoch_k < 20) and (latest_stoch_k > 20),
            
            # Modificación: Condición no se cumple si el volumen anterior es 0
            f"Volumen dominante de compra {emoji if dominant == 'COMPRA' else '🔴'} (Actual: {latest_volume:,.0f}, Anterior: {prev_volume:,.0f})":
                (dominant == "COMPRA") and growing  # growing ya incluye la comprobación prev_buy_volume > 0,
                
        }
            
        # Mostrar info de Supertrend (solo informativo)
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Precio: {latest_close:.4f}")
        print(f"ℹ️ Supertrend: {'🟩' if confirmed_st_direction else '🟥'}"
              f"{'En dirección COMPRA' if confirmed_st_direction else 'En dirección VENTA'} "
              f"(Valor: {confirmed_st_value:.4f}, Diferencia: {st_diff:.4f})")
        print(f"📊 Volumen: {emoji} {vol_type} | {vol_sma_status} {latest_volume_sma:,.0f}")
        #print(f"📊 Volumen: {emoji} {vol_type} {vol_comparison} | {vol_sma_status} {latest_volume_sma:,.0f}")
        

        total = len(conditions_with_values)
        ok = sum(conditions_with_values.values())

        print(f"Condiciones cumplidas: {ok}/{total}")
        for k, v in conditions_with_values.items():
            print(f"{'✔️' if v else '❌'} {k}")

        if ok == total:
            print(f"✅ Señal COMPLETA: Todos los criterios cumplidos. Precio actual: {latest_close:.4f}")
            alert_signal("complete")
        elif ok >= 3:
            print(f"⚠️ Señal Parcial: {ok}/{total} criterios cumplidos. Precio actual: {latest_close:.4f}")
            alert_signal("partial")
        else:
            print(f"❕ Sin señal suficiente: Solo {ok}/{total} criterios cumplidos. Precio actual: {latest_close:.4f}")

    except Exception as e:
        print(f"Error al evaluar lista de verificación: {e}")
        import traceback
        traceback.print_exc()

    try:
        check_trade_status(latest["Close"], entry_params)
    except Exception as e:
        print(f"Error en check_trade_status: {e}")