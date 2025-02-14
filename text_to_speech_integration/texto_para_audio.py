from elevenlabs import stream
from elevenlabs.client import ElevenLabs

# Configuração do cliente ElevenLabs
API_KEY = "sk_5e2539fc5f450aac4c9c69ebb2df8fad379091f08243991e"
client = ElevenLabs(api_key=API_KEY)

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
