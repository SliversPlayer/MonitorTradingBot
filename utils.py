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
    
def load_monitor_config(filepath="monitor_config.txt"):
    """Carga configuración general del monitor desde un archivo de texto"""
    config = {
        "whatsapp_alerts": True,
        "sound_alerts": True
    }
    if not os.path.exists(filepath):
        return config  # Retorna valores por defecto

    try:
        with open(filepath, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    key = key.strip().lower()
                    val = value.strip().lower()
                    if key in config:
                        config[key] = val == "true"
        return config
    except Exception as e:
        print(f"⚠️ Error al leer configuración del monitor: {e}")
        return config    

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