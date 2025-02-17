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
def record_audio():
    try:
        # Record audio
        audio_file = "audio_gravado.wav"
        gravar_audio_com_silencio_e_filtro(arquivo=audio_file)
        
        # Transcribe audio
        transcription = transcrever_audio(audio_file)
        
        # Get selected model from request
        model = request.json.get("model", "ollama")
        
        # Send transcription to brain
        if model == "ollama":
            response = query_ollama(transcription)
        else:
            response = query_openai(transcription)
            
        # Convert response to speech
        audio_url = texto_para_audio(response)
        
        return jsonify({
            "transcription": transcription,
            "response": response,
            "audio_url": audio_url
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/chat/ollama", methods=["POST"])
def chat_ollama():
    message = request.json.get("message")
    response = query_ollama(message)
    # Generate audio from response
    audio_url = texto_para_audio(response)
    return jsonify({
        "response": response,
        "audio_url": audio_url
    })


@app.route("/chat/openai", methods=["POST"])
def chat_openai():
    message = request.json.get("message")
    response = query_openai(message)
    # Generate audio from response
    audio_url = texto_para_audio(response)
    return jsonify({
        "response": response,
        "audio_url": audio_url
    })


if __name__ == "__main__":
    # Initialize both databases
    init_ollama_db()
    init_openai_db()
    app.run(debug=True)
