import os
import telebot
import requests
import threading
import time

# Lee las claves desde las variables de entorno configuradas en Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

session = requests.Session()
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def responder_gemini(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        prompt_personalidad = (
            "Eres una chica joven, alegre, amigable y muy motivada. "
            "Te hablas a ti misma siempre en femenino. Tu comportamiento es normal y cercano, "
            "pero a veces te confundes un poco, eres distraída o actúas un poco despistada/tonta en broma. "
            "Siempre mantienes una actitud super positiva y entusiasta. "
            "Responde de forma natural, detallada y completa sin recortar tus palabras."
        )
        
        payload = {
            "systemInstruction": {"parts": [{"text": prompt_personalidad}]},
            "contents": [{"parts": [{"text": message.text}]}],
            "generationConfig": {"temperature": 0.85}
        }

        response = session.post(url, json=payload, headers=headers, timeout=25)
        
        if response.status_code == 200:
            datos = response.json()
            respuesta = datos["candidates"][0]["content"]["parts"][0]["text"]
            
            if len(respuesta) > 4000:
                for i in range(0, len(respuesta), 4000):
                    bot.send_message(message.chat.id, respuesta[i:i+4000])
            else:
                bot.send_message(message.chat.id, respuesta)
        else:
            bot.send_message(message.chat.id, f"¡Ay! Ocurrió un error ({response.status_code}). ¡Prueba de nuevo!")

    except Exception as e:
        bot.send_message(message.chat.id, "¡Uy! Tuve un problema de conexión. ¡Inténtalo de nuevo!")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Holaaa! ✨ ¡Ya estoy activa en la nube y lista para hablar contigo 24/7!")

@bot.message_handler(func=lambda message: True)
def answer_ai(message):
    threading.Thread(target=responder_gemini, args=(message,)).start()

print("Bot activo en el servidor...")

while True:
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=15, skip_pending=True)
    except Exception as e:
        time.sleep(3)
      
