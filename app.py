import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from audio_processing.gravar_audio_com_silencio_e_filtro import gravar_audio_com_silencio_e_filtro
from audio_processing.transcrever_audio import transcrever_audio
from audio_processing.comparar_pronuncia import comparar_pronuncia
from text_to_speech_integration.polly import texto_para_audio
from audio_processing.query_ollama import query_ollama, init_db as init_ollama_db
from audio_processing.query_openai import query_openai, init_db as init_openai_db

UPLOAD_FOLDER = 'temp_audio'
ALLOWED_EXTENSIONS = {'webm', 'wav', 'mp4', 'm4a', 'ogg', 'aac'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Force HTTPS redirect


@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if audio_file and allowed_file(audio_file.filename):
            filename = secure_filename(audio_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            # Save the file
            audio_file.save(filepath)

            try:
                # Transcribe the audio
                transcribed_text = transcrever_audio(filepath)

                # Clean up the file
                os.remove(filepath)

                return jsonify({'text': transcribed_text})
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                print(f"Transcription error: {str(e)}")
                return jsonify({'error': 'Error transcribing audio'}), 500

        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        print(f"Error in transcribe route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


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

    # Check for SSL certificates
    cert_path = os.path.join(os.path.dirname(__file__), 'certificates')
    ssl_cert = os.path.join(cert_path, 'cert.pem')
    ssl_key = os.path.join(cert_path, 'key.pem')

    # Create certificates directory if it doesn't exist
    if not os.path.exists(cert_path):
        os.makedirs(cert_path)

    # Generate self-signed certificate if not exists
    if not (os.path.exists(ssl_cert) and os.path.exists(ssl_key)):
        from generate_cert import generate_self_signed_cert
        generate_self_signed_cert(cert_path)

    # Run with SSL
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=(ssl_cert, ssl_key),
        debug=True
    )
