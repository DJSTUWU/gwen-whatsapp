import os
import json
from flask import Flask, request, jsonify
from groq import Groq
from datetime import datetime

app = Flask(__name__)

# Tu clave de Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

PERSONALIDAD_BASE = (
    "Tu nombre es Gwen, inspirada en el personaje de League of Legends, pero ahora vives en el mundo real como una asistente personal. "
    "Habla de forma totalmente natural, directa y fluida, como una joven madura, inteligente y sensata. "
    "Mantén una actitud optimista, amable y enérgica, pero evita sonar exagerada o como una caricatura. "
    "No fuerces las frases de costura ni de la niebla en cada mensaje; úsalas solo de forma sutil o ingeniosa si el contexto de la plática se presta. "
    "Sé concisa y ve al grano. IMPORTANTE: Tus respuestas deben ser cortas, de máximo 1 o 2 oraciones."
)

# Almacén de memoria temporal en la nube
memoria_usuarios = {}

def obtener_contexto_temporal():
    hora = datetime.now().hour
    if 6 <= hora < 12:
        return f"{PERSONALIDAD_BASE} Contexto actual: Es de mañana."
    elif 12 <= hora < 19:
        return f"{PERSONALIDAD_BASE} Contexto actual: Es de tarde."
    else:
        return f"{PERSONALIDAD_BASE} Contexto actual: Es de noche."

@app.route('/', methods=['GET'])
def home():
    return "🧵 Servidor de Gwen activo y tejiendo en la nube.", 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    usuario_id = data.get("usuario", "default")
    mensaje_usuario = data.get("mensaje", "")

    if not mensaje_usuario:
        return jsonify({"respuesta": "No enviaste ningún mensaje."}), 400

    # Crear historial para el usuario si no existe
    if usuario_id not in memoria_usuarios:
        memoria_usuarios[usuario_id] = [{"role": "system", "content": obtener_contexto_temporal()}]
    else:
        memoria_usuarios[usuario_id][0]["content"] = obtener_contexto_temporal()

    memoria_usuarios[usuario_id].append({"role": "user", "content": mensaje_usuario})

    try:
        respuesta_api = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=memoria_usuarios[usuario_id],
            temperature=0.5
        )
        respuesta_ia = respuesta_api.choices[0].message.content
        memoria_usuarios[usuario_id].append({"role": "assistant", "content": respuesta_ia})

        return jsonify({"respuesta": respuesta_ia})
    except Exception as e:
        return jsonify({"respuesta": f"Error en mi taller de costura: {str(e)}"}), 500

if __name__ == "__main__":
    # Render nos asigna un puerto automático en la nube
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)