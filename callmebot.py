import requests
import os

def load_credentials(filepath="callmebot_credentials.txt"):
    """Carga número y API key desde un archivo"""
    credentials = {}
    try:
        with open(filepath, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    credentials[key.strip()] = value.strip()
        return credentials
    except Exception as e:
        print(f"⚠️ Error al cargar credenciales de CallMeBot: {e}")
        return {}

def send_callmebot_message(message):
    """
    Envía un mensaje de WhatsApp usando CallMeBot a tu número verificado.
    """
    creds = load_credentials()
    phone = creds.get("phone")
    apikey = creds.get("apikey")

    if not phone or not apikey:
        print("❌ Credenciales CallMeBot no configuradas correctamente.")
        return

    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={apikey}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Mensaje enviado con CallMeBot.")
        else:
            print(f"❌ Error al enviar mensaje: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción durante el envío con CallMeBot: {e}")

