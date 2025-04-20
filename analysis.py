# analysis.py
"""
Módulo para analizar datos y generar señales
"""
from datetime import datetime
from utils import alert_signal
from config import SYMBOL, VOLUME_SMA_PERIOD
from callmebot import send_callmebot_message
from utils import alert_signal, load_monitor_config

monitor_config = load_monitor_config()

def check_trade_status(latest_close, entry_params):
    """Verifica el estado de una operación en curso"""
    message = ""
    try:
        if "entry_price" not in entry_params or not entry_params["entry_price"]:
            message = "📌 No se ha definido un precio de entrada en el archivo. No se realizará seguimiento."
            print(message)
            return message

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
        return result

    except Exception as e:
        message = f"Error en seguimiento de operación: {e}"
        print(message)
        return message

def safe_get(series, key, default=0):
    """Obtiene un valor de forma segura de una Series, devolviendo un default si hay error"""
    try:
        return series[key]
    except (KeyError, IndexError, TypeError):
        print(f"⚠️ No se encontró el indicador '{key}'. Usando valor predeterminado.")
        return default

def interpretar_market_state(latest):
    """Interpreta y genera un mensaje descriptivo del estado del mercado"""
    market_state = safe_get(latest, "MARKET_STATE", "UNKNOWN")
    atr_pct = safe_get(latest, "ATR_pct", 0) * 100
    adx = safe_get(latest, "ADX", 0)
    ema9 = safe_get(latest, "EMA9", 0)
    ema21 = safe_get(latest, "EMA21", 0)
    ema100 = safe_get(latest, "EMA100", 0)

    texto_estado = {
        "BULLISH": "Tendencia alcista confirmada",
        "BEARISH": "Tendencia bajista confirmada",
        "LATERAL": "Consolidación con baja volatilidad",
        "TRANSITION": "Cambio de fase en proceso",
        "UNKNOWN": "Estado no definido"
    }.get(market_state, "Estado no definido")

    if ema9 > ema21 > ema100:
        ema_estructura = "EMA9 > EMA21 > EMA100"
    elif ema9 < ema21 < ema100:
        ema_estructura = "EMA9 < EMA21 < EMA100"
    else:
        ema_estructura = f"desordenadas (EMA9 {'>' if ema9 > ema21 else '<'} EMA21 {'>' if ema21 > ema100 else '<'} EMA100)"

    emoji_state = {
        "BULLISH": "📈", "BEARISH": "📉",
        "LATERAL": "⏸️", "TRANSITION": "🔁",
        "UNKNOWN": "❓"
    }.get(market_state, "❓")

    msg_context = (
        f"🧽 Contexto del mercado: {emoji_state} {market_state} {texto_estado}\n"
        f"   ├ ATR%: {atr_pct:.2f}% (umbral: <1.50%)\n"
        f"   ├ ADX : {adx:.1f}   (umbral: <20)\n"
        f"   └ EMAs: {ema_estructura}\n"
    )
    return msg_context, market_state

def evaluate_checklist(df, entry_params):
    """Evalúa las condiciones de trading basadas en los indicadores"""
    # Variable para construir el mensaje
    message = ""
    try:
        if len(df) < 3:
            message = "No hay suficientes datos para evaluar la lista de verificación"
            print(message)
            return message

        latest = df.iloc[-1]
        previous = df.iloc[-2]
        before_previous = df.iloc[-3]
        
        # Obtener e interpretar el estado del mercado
        market_context_msg, market_state = interpretar_market_state(latest)
        message += market_context_msg

        # Extraer valores (usando safe_get para evitar KeyError)
        latest_close = latest["Close"]
        latest_ema9 = safe_get(latest, "EMA9", latest_close * 0.95)
        latest_ema20 = safe_get(latest, "EMA20", latest_close * 0.90)
        compare_latest_ema9 = latest_close > latest_ema9
        compare_latest_ema20 = latest_close > latest_ema20
        ema9_20_direction = "⬆️" if (compare_latest_ema9 and compare_latest_ema20) else "⬇️"
        
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
        
        # Mostrar info de Supertrend (solo informativo)
        timestamp = datetime.now().strftime('%H:%M:%S')
        msg_part1 = f"\n[{timestamp}] Precio: {latest_close:.4f}\n"
        msg_part2 = f"ℹ️ Supertrend: {'🟩' if confirmed_st_direction else '🟥'} "
        msg_part2 += f"{'En dirección COMPRA' if confirmed_st_direction else 'En dirección VENTA'} "
        msg_part2 += f"(Valor: {confirmed_st_value:.4f}, Diferencia: {st_diff:.4f})\n"
        msg_part3 = f"📊 Volumen: {emoji} {vol_type} | {vol_sma_status} {latest_volume_sma:,.0f}\n"
        
        # Agregar al mensaje y mostrar
        message += msg_part1 + msg_part2 + msg_part3
        print(msg_part1, end="")
        print(msg_part2, end="")
        print(msg_part3, end="")

        # Incluir el estado del mercado en las condiciones evaluadas
        conditions_with_values = {
            f"EMA9 y EMA20 {ema9_20_direction} precio (EMA9: {latest_ema9:.4f}, EMA20: {latest_ema20:.4f})":
                (compare_latest_ema9) and (compare_latest_ema20),
        
            f"MACD > Signal {macd_direction} (MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}, Histo: {histogram_macd:.4f})":
                latest_macd > latest_macd_signal,
        
            f"RSI < 60 y subiendo (RSI actual: {latest_rsi:.2f}, RSI Prev: {prev_rsi:.2f})":
                (latest_rsi < 60) and (latest_rsi > prev_rsi),
        
            f"Stoch RSI %K cruza 20 al alza (K actual: {latest_stoch_k:.2f}, K Prev: {prev_stoch_k:.2f})":
                (prev_stoch_k < 20) and (latest_stoch_k > 20),
            
            # Modificación: Condición no se cumple si el volumen anterior es 0
            f"Volumen dominante de compra {emoji if dominant == 'COMPRA' else '🔴'} (Actual: {latest_volume:,.0f}, Anterior: {prev_volume:,.0f})":
                (dominant == "COMPRA") and growing,  # growing ya incluye la comprobación prev_buy_volume > 0
                
            # Nueva condición: Estado del mercado favorable para operar
            f"Estado del mercado ({market_state})":
                market_state in ["BULLISH", "TRANSITION"]  # Considerar favorable en tendencia alcista o transición
        }
            
        total = len(conditions_with_values)
        ok = sum(conditions_with_values.values())

        msg_conditions_header = f"Condiciones cumplidas: {ok}/{total}\n"
        message += msg_conditions_header
        print(msg_conditions_header, end="")
        
        # Construir y mostrar cada condición
        for k, v in conditions_with_values.items():
            condition_line = f"{'✔️' if v else '❌'} {k}\n"
            message += condition_line
            print(condition_line, end="")

        # Ajustar umbrales según el estado del mercado
        signal_threshold_full = total
        signal_threshold_partial = 3
        
        # En mercado lateral ser más estricto
        if market_state == "LATERAL":
            signal_threshold_full = total  # Exigir todas las condiciones
        # En mercado alcista ser menos estricto
        elif market_state == "BULLISH":
            signal_threshold_full = total - 1  # Permitir que falle una condición
            signal_threshold_partial = 3
        # En mercado bajista ser más cauteloso con señales de compra
        elif market_state == "BEARISH":
            signal_threshold_full = total  # Exigir todas las condiciones
            signal_threshold_partial = 4   # Exigir más condiciones para señal parcial

        # Construir y mostrar la conclusión del análisis
        if ok >= signal_threshold_full:
            result_line = f"✅ Señal COMPLETA: {ok}/{total} criterios cumplidos en mercado {market_state}. Precio actual: {latest_close:.4f}\n"
            message += result_line
            print(result_line, end="")
            if monitor_config.get("sound_alerts"):
                alert_signal("complete")
            if monitor_config.get("whatsapp_alerts"):
                send_callmebot_message(f"🚨 ALERTA COMPRA {SYMBOL}\n\n{message}")
        elif ok >= signal_threshold_partial:
            result_line = f"⚠️ Señal Parcial: {ok}/{total} criterios cumplidos en mercado {market_state}. Precio actual: {latest_close:.4f}\n"
            message += result_line
            print(result_line, end="")
            if monitor_config.get("sound_alerts"):
                alert_signal("complete")
            if monitor_config.get("whatsapp_alerts"):
                send_callmebot_message(f"🚨 ALERTA COMPRA {SYMBOL}\n\n{message}")
        else:
            result_line = f"❕ Sin señal suficiente en mercado {market_state}: Solo {ok}/{total} criterios cumplidos.\n"
            message += result_line
            print(result_line, end="")
        

        print(market_context_msg, end="")
        
    except Exception as e:
        error_msg = f"Error al evaluar lista de verificación: {e}\n"
        message += error_msg
        print(error_msg, end="")
        import traceback
        traceback.print_exc()

    try:
        trade_status = check_trade_status(latest["Close"], entry_params)
        message += trade_status
    except Exception as e:
        error_msg = f"Error en check_trade_status: {e}\n"
        message += error_msg
        print(error_msg, end="")
    
    return message