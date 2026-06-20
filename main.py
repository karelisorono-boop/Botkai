import os
import threading
import requests
import telebot
from flask import Flask

# --- INICIALIZACIÓN DE CONFIGURACIÓN ---
# Usamos variables de entorno por seguridad, se configuran en el panel de Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
KINDROID_API_KEY = os.environ.get("KINDROID_API_KEY")
KINDROID_AI_ID = os.environ.get("KINDROID_AI_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Crear un servidor web Flask falso para engañar a Render y que no apague el bot
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot en línea 24/7"

def consultar_kindroid(mensaje_usuario):
    url = "https://kindroid.ai"
    headers = {
        "Authorization": f"Bearer {KINDROID_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "ai_id": KINDROID_AI_ID,
        "message": mensaje_usuario
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            respuesta_texto = response.text.strip()
            return respuesta_texto if respuesta_texto else "Tu Kindroid envió una respuesta vacía."
        else:
            return f"Error de Kindroid (Código {response.status_code}): {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def enviar_bienvenida(message):
    bot.reply_to(message, "¡Conexión en la nube establecida con éxito! Envíame un mensaje.")

@bot.message_handler(func=lambda message: True)
def manejar_mensaje(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
    except:
        pass
    respuesta_ai = consultar_kindroid(message.text)
    bot.reply_to(message, respuesta_ai)

def run_bot():
    print("Iniciando conexión con Telegram...")
    bot.infinity_polling(non_stop=True, timeout=20)

if __name__ == "__main__":
    # Arrancar el bot de Telegram en un hilo separado
    threading.Thread(target=run_bot, daemon=True).start()
    # Arrancar el servidor web en el puerto que pide Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
