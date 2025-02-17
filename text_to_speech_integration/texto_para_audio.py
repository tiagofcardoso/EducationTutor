from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(
    dotenv_path='/home/tiagocardoso/Projects/EducationTutor/audio_processing/api_keys/.env')


# Configuração do cliente ElevenLabs
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Função para síntese de fala com ElevenLabs


def texto_para_audio(texto,
                     voice_id="D38z5RcWu1voky8WS1ja", 
                     model_id="eleven_multilingual_v2"):
    audio_stream = client.text_to_speech.convert_as_stream(
        text=texto,
        voice_id=voice_id,
        model_id=model_id
    )

    # Reproduzir o áudio gerado
    stream(audio_stream)
