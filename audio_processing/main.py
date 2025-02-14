from gravar_audio_com_silencio_e_filtro import gravar_audio_com_silencio_e_filtro
from transcrever_audio import transcrever_audio
from comparar_pronuncia import comparar_pronuncia
from text_to_speech_integration.texto_para_audio import texto_para_audio

def main():
    frase_esperada = "Olá! Vamos praticar a sua pronúncia hoje?"

    # Captura de áudio com detecção de silêncio
    audio_path = gravar_audio_com_silencio_e_filtro()

    # Transcrição do áudio capturado
    texto_transcrito = transcrever_audio(audio_path)
    print(f"Texto transcrito: {texto_transcrito}")

    # Comparação da pronúncia
    feedback = comparar_pronuncia(frase_esperada, texto_transcrito)
    print(feedback)

    # Fornecendo feedback em áudio
    texto_para_audio(feedback)


if __name__ == "__main__":
    main()
