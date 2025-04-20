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

        latest_rsi = safe_get(latest, "RSI", 50)
        prev_rsi = safe_get(previous, "RSI", 50)

        latest_stoch_k = safe_get(latest, "Stoch_K", 50)
        prev_stoch_k = safe_get(previous, "Stoch_K", 50)

        latest_volume = latest["Volume"]
        prev_volume = previous["Volume"]
        latest_volume_sma = safe_get(latest, "Volume_SMA", latest_volume * 0.9)
        
        # Volumen comprador y vendedor
        latest_buy_volume = safe_get(latest, "BuyVolume")
        prev_buy_volume = safe_get(previous, "BuyVolume")
        latest_sell_volume = safe_get(latest, "SellVolume")
        prev_sell_volume = safe_get(previous, "SellVolume")
        buy_volume_sma = safe_get(latest, "BuyVolume_SMA")
        
        # Determinar volumen dominante actual
        if latest_buy_volume >= latest_sell_volume:
            dominant = "COMPRA"
            emoji = "🟢"
            vol_current = latest_buy_volume
        else:
            dominant = "VENTA"
            emoji = "🔴"
            vol_current = latest_sell_volume

        # Determinar volumen dominante anterior (sea de compra o venta)
        if prev_buy_volume >= prev_sell_volume:
            prev_dominant = "COMPRA"
            prev_emoji = "🟢"
            vol_prev = prev_buy_volume
        else:
            prev_dominant = "VENTA"
            prev_emoji = "🔴"
            vol_prev = prev_sell_volume
        
        # Verificar si el volumen está creciendo en su categoría
        growing = False
        if dominant == "COMPRA" and prev_dominant == "COMPRA":
            growing = latest_buy_volume > prev_buy_volume * 1.1 and prev_buy_volume > 0
        elif dominant == "VENTA" and prev_dominant == "VENTA":
            growing = latest_sell_volume > prev_sell_volume * 1.1 and prev_sell_volume > 0
        
        # Versión simplificada en una sola línea
        vol_change_emoji = "+" if growing else "-"
        vol_comparison = f"{vol_change_emoji} ({vol_current:,.0f} vs {vol_prev:,.0f})"
        vol_sma_status = "↑SMA" if vol_current > buy_volume_sma else "↓SMA"
        
        # Supertrend confirmado en vela cerrada (solo informativo)
        confirmed_st_direction = safe_get(previous, "Supertrend_Direction", True)
        confirmed_st_value = safe_get(previous, "Supertrend", latest_close)

        # Dirección del precio
        price_direction = "⬆️" if latest_close > previous["Close"] else "⬇️"
        macd_direction = "⬆️" if latest_macd > prev_macd else "⬇️"

        # Verificación de volumen dominante para la condición:
        # - La condición se cumple sólo si:
        #   1. El volumen dominante es de COMPRA en la vela actual
        #   2. El volumen dominante también fue de COMPRA en la vela anterior
        #   3. El volumen de compra actual es mayor que el volumen de compra anterior
        vol_condition_met = (dominant == "COMPRA" and  # Volumen actual es dominante de compra
                            prev_dominant == "COMPRA" and  # Volumen anterior también era dominante de compra
                            latest_buy_volume > prev_buy_volume * 1.1 and  # Hay crecimiento del volumen de compra
                            prev_buy_volume > 0)  # Prevenir división por cero
        
        vol_condition_text = f"Volumen dominante de compra creciente {emoji} (Actual: {latest_buy_volume:.0f}, Anterior: {prev_buy_volume:.0f})"

        conditions_with_values = {
            f"Precio sobre EMA9 y EMA20 {price_direction} (Precio: {latest_close:.4f}, EMA9: {latest_ema9:.4f}, EMA20: {latest_ema20:.4f})":
                (latest_close > latest_ema9) and (latest_close > latest_ema20),
        
            f"MACD > Signal {macd_direction} (MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}, MACD Anterior: {prev_macd:.4f})":
                latest_macd > latest_macd_signal,
        
            f"RSI < 60 y subiendo (RSI actual: {latest_rsi:.2f}, RSI anterior: {prev_rsi:.2f})":
                (latest_rsi < 60) and (latest_rsi > prev_rsi),
        
            f"Stoch RSI %K cruza 20 al alza (K actual: {latest_stoch_k:.2f}, K anterior: {prev_stoch_k:.2f})":
                (prev_stoch_k < 20) and (latest_stoch_k > 20),
            
            vol_condition_text: vol_condition_met
        }
            
        # Mostrar info de Supertrend (solo informativo)
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}]ℹ️ Supertrend: {'🟩' if confirmed_st_direction else '🟥'} "
              f"{'En dirección COMPRA' if confirmed_st_direction else 'En dirección VENTA'} "
              f"(Valor: {confirmed_st_value:.4f})")
        
        print(f"📊 Volumen: {emoji} {dominant} {vol_comparison} | {vol_sma_status} {latest_volume_sma:.2f}")

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

    try:
        check_trade_status(latest["Close"], entry_params)
    except Exception as e:
        print(f"Error en check_trade_status: {e}")