import whisper
import os

# Função para transcrever áudio usando Whisper


def transcrever_audio(arquivo):
    try:
        # Check if file exists
        if not os.path.exists(arquivo):
            raise FileNotFoundError(f"Audio file not found: {arquivo}")

        # Load model with specific device placement
        modelo = whisper.load_model("base")

        # Transcribe with additional parameters for better results
        resultado = modelo.transcribe(
            arquivo,
            language="pt",  # Set to Portuguese
            fp16=False,     # Disable half-precision to avoid some GPU issues
            verbose=True    # Enable verbose output for debugging
        )

        return resultado['text']
    except Exception as e:
        print(f"Error in transcrever_audio: {str(e)}")
        raise
