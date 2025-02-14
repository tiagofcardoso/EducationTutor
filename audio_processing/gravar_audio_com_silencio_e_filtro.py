import pyaudio
import wave
import numpy as np
import noisereduce as nr
import time


def gravar_audio_com_silencio_e_filtro(arquivo="audio_gravado.wav", duracao_max=60, limite_silencio=500, tempo_silencio=5):
    formato = pyaudio.paInt16
    canais = 1
    taxa_amostragem = 16000
    largura_amostra = 2

    p = pyaudio.PyAudio()
    stream = p.open(format=formato,
                    channels=canais,
                    rate=taxa_amostragem,
                    input=True,
                    frames_per_buffer=1024)

    print("Gravando...")

    frames = []
    silencio_contador = 0
    tempo_inicio = time.time()

    while True:
        dados = stream.read(1024)
        frames.append(dados)

        # Converter os dados em uma array numpy para cálculo de volume
        audio = np.frombuffer(dados, dtype=np.int16)

        # Redução de ruído utilizando o noisereduce
        audio_reduzido = nr.reduce_noise(y=audio, sr=taxa_amostragem)

        # Calcular a energia (volume) média do áudio
        volume = np.sqrt(np.mean(audio_reduzido**2))

        # Se o volume for menor que o limite de silêncio, incrementar o contador
        if volume < limite_silencio:
            silencio_contador += 1
        else:
            silencio_contador = 0

        # Verifica o tempo de silêncio contínuo
        if silencio_contador > (taxa_amostragem / 1024) * tempo_silencio:
            print("Silêncio detectado. Parando a gravação...")
            break

        # Se o tempo máximo de gravação for alcançado, parar a gravação
        if time.time() - tempo_inicio > duracao_max:
            print("Tempo máximo de gravação atingido.")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Salvar o arquivo
    with wave.open(arquivo, 'wb') as wf:
        wf.setnchannels(canais)
        wf.setsampwidth(largura_amostra)
        wf.setframerate(taxa_amostragem)
        wf.writeframes(b''.join(frames))

    return arquivo


# Teste
if __name__ == "__main__":
    audio_path = gravar_audio_com_silencio_e_filtro()
    print(f"Áudio gravado em: {audio_path}")
