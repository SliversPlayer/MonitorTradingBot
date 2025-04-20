# data.py
"""
Módulo para obtener y procesar datos de precios
"""
import pandas as pd

def fetch_ohlcv_data(exchange, symbol, timeframe, limit):
    """Obtiene datos OHLCV del exchange y los retorna como DataFrame"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching OHLCV data: {e}")
        return pd.DataFrame()
