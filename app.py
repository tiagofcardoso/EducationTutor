from flask import Flask, render_template, request, jsonify
from audio_processing.gravar_audio_com_silencio_e_filtro import gravar_audio_com_silencio_e_filtro
from audio_processing.transcrever_audio import transcrever_audio
from audio_processing.comparar_pronuncia import comparar_pronuncia
from text_to_speech_integration.texto_para_audio import texto_para_audio
from audio_processing.brain_ollama import query_ollama, init_db as init_ollama_db
from audio_processing.brain_openai import query_openai, init_db as init_openai_db

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/record", methods=["POST"])
def record():
    frase_esperada = "Olá! Vamos praticar a sua pronúncia hoje?"

    # Captura do áudio com detecção de silêncio
    audio_path = gravar_audio_com_silencio_e_filtro()

    # Transcreve o áudio
    texto_transcrito = transcrever_audio(audio_path)

    # Gera o feedback comparando com a frase esperada
    feedback = comparar_pronuncia(frase_esperada, texto_transcrito)

    # Gera o áudio de resposta usando ElevenLabs e retorna o caminho do arquivo
    audio_url = texto_para_audio(feedback)

    return jsonify({
        "transcription": texto_transcrito,
        "feedback": feedback,
        "audio_url": audio_url
    })


@app.route("/chat/ollama", methods=["POST"])
def chat_ollama():
    message = request.json.get("message")
    response = query_ollama(message)
    return jsonify({"response": response})


@app.route("/chat/openai", methods=["POST"])
def chat_openai():
    message = request.json.get("message")
    response = query_openai(message)
    return jsonify({"response": response})


if __name__ == "__main__":
    # Initialize both databases
    init_ollama_db()
    init_openai_db()
    app.run(debug=True)
