# utils.py
"""
Módulo con funciones de utilidad
"""
import os
import platform

# Comprobación para sistemas que no soportan winsound
if platform.system() == 'Windows':
    import winsound
else:
    # Dummy function para sistemas no Windows
    def winsound():
        class DummyBeep:
            @staticmethod
            def Beep(frequency, duration):
                print(f"[BEEP] Frecuencia: {frequency}, Duración: {duration}")
        return DummyBeep()
    winsound = winsound()

def load_entry_params(filepath="entry.txt"):
    """Carga parámetros de entrada desde un archivo"""
    if not os.path.exists(filepath):
        print(f"Archivo {filepath} no encontrado. Creando uno nuevo con valores predeterminados.")
        with open(filepath, "w") as f:
            f.write("entry_price=0.6300\ntake_profit=0.6380\nstop_loss=0.6215\n")
        
    try:
        params = {}
        with open(filepath, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if value:  # Solo procesar si hay un valor
                        try:
                            params[key] = float(value)
                        except ValueError:
                            print(f"Error al convertir {value} a número para {key}")
        
        # Verificar que existan los parámetros esperados
        if "entry_price" not in params or params["entry_price"] == 0:
            print("⚠️ Advertencia: No se encontró un precio de entrada válido en entry.txt")
            
        return params
    except Exception as e:
        print(f"Error al leer {filepath}: {e}")
        return {"entry_price": 0.6300, "take_profit": 0.6380, "stop_loss": 0.6215}

def alert_signal(signal_type):
    """Genera una alerta sonora según el tipo de señal"""
    try:
        if signal_type == "complete":
            if platform.system() == 'Windows':
                winsound.Beep(1200, 500)
                winsound.Beep(1400, 500)
                winsound.Beep(1700, 500)
            else:
                print("🔊 [ALERTA COMPLETA] ¡Todos los criterios cumplidos!")
        elif signal_type == "partial":
            if platform.system() == 'Windows':
                winsound.Beep(1200, 500)
            else:
                print("🔊 [ALERTA PARCIAL] Algunos criterios cumplidos")
    except Exception as e:
        print(f"⚠️ No se pudo reproducir el sonido: {e}")