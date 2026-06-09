import os
import telebot
from groq import Groq

# Traemos las llaves desde el sistema de Render en secreto
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

PERSONALIDAD_BASE = (
    "Tu nombre es Gwen, inspirada en el personaje de League of Legends, pero ahora vives en el mundo real como una asistente personal. "
    "Habla de forma totalmente natural, directa y fluida, como una joven madura, inteligente y sensata. "
    "Mantén una actitud optimista, amable y enérgica, pero evita sonar exagerada o como una caricatura. "
    "No fuerces las frases de costura en cada mensaje; úsalas solo de sutil forma si el contexto se presta. "
    "Sé concisa y ve al grano. Respuestas cortas, de máximo 1 o 2 oraciones."
)

memoria_usuarios = {}

@bot.message_handler(func=lambda message: True)
def responder_chat(message):
    usuario_id = str(message.chat.id)
    mensaje_usuario = message.text

    if usuario_id not in memoria_usuarios:
        memoria_usuarios[usuario_id] = [{"role": "system", "content": PERSONALIDAD_BASE}]

    memoria_usuarios[usuario_id].append({"role": "user", "content": mensaje_usuario})

    try:
        respuesta_api = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=memoria_usuarios[usuario_id],
            temperature=0.5
        )
        respuesta_ia = respuesta_api.choices[0].message.content
        memoria_usuarios[usuario_id].append({"role": "assistant", "content": respuesta_ia})
        
        bot.reply_to(message, respuesta_ia)
    except Exception as e:
        bot.reply_to(message, f"Hubo un detalle en mi taller de costura: {str(e)}")

if __name__ == "__main__":
    print("🧵 Gwen está escuchando en Telegram...")
    bot.infinity_polling()