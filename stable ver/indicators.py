# indicators.py
"""
Módulo para calcular indicadores técnicos
"""
import pandas as pd
import ta
import numpy as np

def calculate_indicators(df, config=None):
    """
    Calcula indicadores técnicos para un DataFrame de OHLCV
    
    Args:
        df: DataFrame con datos OHLCV
        config: Diccionario opcional con configuración para los indicadores
    """
    if df.empty:
        print("Error: DataFrame vacío. Compruebe la conexión o el símbolo.")
        return df
    
    try:
        df_copy = df.copy()
        
        # Valores por defecto si no se proporciona configuración
        if config is None:
            config = {
                'SUPERTREND_PERIOD': 10,
                'SUPERTREND_MULTIPLIER': 3,
                'RSI_PERIOD': 14,
                'EMA_PERIODS': [9, 20, 100],
                'VOLUME_SMA_PERIOD': 20
            }

        # EMA
        ema_periods = config.get('EMA_PERIODS', [9, 20, 100])
        for period in ema_periods:
            df_copy[f"EMA{period}"] = ta.trend.ema_indicator(df_copy["Close"], window=period)

        # RSI
        rsi_period = config.get('RSI_PERIOD', 14)
        df_copy["RSI"] = ta.momentum.RSIIndicator(df_copy["Close"], window=rsi_period).rsi()

        # Stoch RSI %K y %D
        stoch_rsi = ta.momentum.StochRSIIndicator(df_copy["Close"])
        df_copy["Stoch_K"] = stoch_rsi.stochrsi_k() * 100
        df_copy["Stoch_D"] = stoch_rsi.stochrsi_d() * 100

        # MACD y señal
        macd = ta.trend.MACD(df_copy["Close"])
        df_copy["MACD"] = macd.macd()
        df_copy["MACD_Signal"] = macd.macd_signal()

        # Volumen SMA
        vol_sma_period = config.get('VOLUME_SMA_PERIOD', 20)
        df_copy["Volume_SMA"] = df_copy["Volume"].rolling(window=vol_sma_period).mean()

        # Supertrend simplificado
        st_period = config.get('SUPERTREND_PERIOD', 10)
        st_multiplier = config.get('SUPERTREND_MULTIPLIER', 3)
        df_copy = calculate_supertrend_simple(df_copy, period=st_period, multiplier=st_multiplier)

        # Rellenar valores faltantes
        df_copy = df_copy.bfill().ffill()

        return df_copy

    except Exception as e:
        print(f"Error al calcular indicadores: {e}")
        import traceback
        traceback.print_exc()
        return df

def calculate_supertrend_simple(df, period=10, multiplier=3):
    """
    Versión simplificada del cálculo de Supertrend
    """
    try:
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        
        # Calcular True Range
        tr1 = np.abs(high - low)
        tr2 = np.abs(high - np.roll(close, 1))
        tr2[0] = tr1[0]  # Fix para el primer valor
        tr3 = np.abs(low - np.roll(close, 1))
        tr3[0] = tr1[0]  # Fix para el primer valor
        
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Calcular ATR
        atr = np.zeros_like(close)
        atr[0:period] = np.mean(true_range[0:period])
        for i in range(period, len(atr)):
            atr[i] = (atr[i-1] * (period-1) + true_range[i]) / period
        
        # Calcular bandas
        hl2 = (high + low) / 2
        upper_band = hl2 + multiplier * atr
        lower_band = hl2 - multiplier * atr
        
        # Inicializar supertrend
        supertrend = np.zeros_like(close)
        direction = np.ones_like(close, dtype=bool)  # True = up/bullish, False = down/bearish
        
        # Primer valor
        supertrend[0] = lower_band[0]
        
        # Calcular supertrend
        for i in range(1, len(close)):
            # Si el precio cierra por encima de la banda superior anterior
            if close[i-1] <= upper_band[i-1]:
                upper_band[i] = min(upper_band[i], upper_band[i-1])
            
            # Si el precio cierra por debajo de la banda inferior anterior
            if close[i-1] >= lower_band[i-1]:
                lower_band[i] = max(lower_band[i], lower_band[i-1])
            
            # Determinar dirección y valor de supertrend
            if supertrend[i-1] == upper_band[i-1] and close[i] <= upper_band[i]:
                supertrend[i] = upper_band[i]
                direction[i] = False
            elif supertrend[i-1] == upper_band[i-1] and close[i] > upper_band[i]:
                supertrend[i] = lower_band[i]
                direction[i] = True
            elif supertrend[i-1] == lower_band[i-1] and close[i] >= lower_band[i]:
                supertrend[i] = lower_band[i]
                direction[i] = True
            elif supertrend[i-1] == lower_band[i-1] and close[i] < lower_band[i]:
                supertrend[i] = upper_band[i]
                direction[i] = False
            else:
                supertrend[i] = supertrend[i-1]
                direction[i] = direction[i-1]
        
        # Agregar al dataframe
        df['Supertrend'] = supertrend
        df['Supertrend_Direction'] = direction
        
        return df
    except Exception as e:
        print(f"Error en cálculo de Supertrend simplificado: {e}")
        import traceback
        traceback.print_exc()
        # Si hay error, crear columnas para evitar KeyError en analysis.py
        df['Supertrend'] = df['Close']
        df['Supertrend_Direction'] = True
        return df