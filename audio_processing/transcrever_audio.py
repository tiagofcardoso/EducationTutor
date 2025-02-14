import whisper

# Função para transcrever áudio usando Whisper


def transcrever_audio(arquivo):
    modelo = whisper.load_model("base")  # Carregar o modelo do Whisper
    resultado = modelo.transcribe(arquivo)
    return resultado['text']
