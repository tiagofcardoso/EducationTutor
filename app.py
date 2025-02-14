from flask import Flask, render_template, request, jsonify
from audio_processing.gravar_audio_com_silencio_e_filtro import gravar_audio_com_silencio_e_filtro
from audio_processing.transcrever_audio import transcrever_audio
from audio_processing.comparar_pronuncia import comparar_pronuncia
from text_to_speech_integration.texto_para_audio import texto_para_audio

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


if __name__ == "__main__":
    app.run(debug=True)
