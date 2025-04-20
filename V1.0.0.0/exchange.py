# exchange.py
"""
Módulo para manejar la conexión con el exchange
"""
import ccxt

def get_exchange(exchange_name):
    """Inicializa y retorna el objeto exchange"""
    try:
        exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})
        return exchange
    except Exception as e:
        print(f"Error initializing exchange: {e}")
        return None

def validate_symbol(exchange, symbol):
    """Valida si el símbolo está disponible en el exchange"""
    try:
        exchange.load_markets()
        if symbol not in exchange.symbols:
            print(f"El símbolo {symbol} no está disponible en {exchange.id}.")
            similar_symbols = [s for s in exchange.symbols if symbol.split('/')[0] in s][:5]
            print(f"Símbolos similares disponibles: {similar_symbols}")
            return False
        return True
    except Exception as e:
        print(f"Error al cargar mercados: {e}")
        return False
