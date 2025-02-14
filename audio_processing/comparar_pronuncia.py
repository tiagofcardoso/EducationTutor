# Função de Feedback de Pronúncia
def comparar_pronuncia(frase_esperada, texto_transcrito):
    if frase_esperada.lower() == texto_transcrito.lower():
        return "Ótima pronúncia! Continue assim!"
    else:
        return f"Você disse: {texto_transcrito}. Tente novamente e fale mais claramente."
