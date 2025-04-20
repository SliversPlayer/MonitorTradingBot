# utils.py
"""
Módulo con funciones de utilidad
"""
import os
import winsound

def load_entry_params(filepath="entry.txt"):
    """Carga parámetros de entrada desde un archivo"""
    if not os.path.exists(filepath):
        return {}
    try:
        params = {}
        with open(filepath, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    try:
                        params[key.strip()] = float(value.strip())
                    except ValueError:
                        pass
        return params
    except Exception as e:
        print(f"Error al leer {filepath}: {e}")
        return {}

def alert_signal(signal_type):
    """Genera una alerta sonora según el tipo de señal"""
    try:
        if signal_type == "complete":
            winsound.Beep(1200, 500)
            winsound.Beep(1400, 500)
            winsound.Beep(1700, 500)
        elif signal_type == "partial":
            winsound.Beep(1200, 500)
    except Exception as e:
        print(f"⚠️ No se pudo reproducir el sonido: {e}")