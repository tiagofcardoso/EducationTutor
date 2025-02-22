from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(
    dotenv_path='/home/tiagocardoso/Projects/EducationTutor/audio_processing/api_keys/.env')

# Configuração do cliente ElevenLabs
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


def texto_para_audio(texto, voice_id="D38z5RcWu1voky8WS1ja", model_id="eleven_multilingual_v2", arquivo="static/audio/response.mp3"):
    try:
        audio_stream = client.text_to_speech.convert_as_stream(
            text=texto,
            voice_id=voice_id,
            model_id=model_id
        )
        # Salvar o áudio em um arquivo
        with open(arquivo, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
        return arquivo
    except Exception as e:
        print(f"Erro ao gerar áudio com ElevenLabs: {e}")
        return None
