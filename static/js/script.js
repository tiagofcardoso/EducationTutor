let avatarIdleAnimation, avatarSpeakingAnimation;
let isSpeaking = false;  // controle se TTS está em reprodução

document.addEventListener("DOMContentLoaded", function () {
    // Carrega o avatar em modo idle
    loadAvatarIdle();
});

// Carrega a animação idle
function loadAvatarIdle() {
    // Se já existir uma animação falando, destruímos
    if (avatarSpeakingAnimation) {
        avatarSpeakingAnimation.destroy();
        avatarSpeakingAnimation = null;
    }

    avatarIdleAnimation = lottie.loadAnimation({
        container: document.getElementById("avatar-container"),
        renderer: "svg",
        loop: true,
        autoplay: true,
        path: "static/animations/talking_et_urso.json" // Ajuste para o seu arquivo de avatar idle
    });
}

// Carrega a animação speaking
function loadAvatarSpeaking() {
    // Se já existir animação idle, destruímos
    if (avatarIdleAnimation) {
        avatarIdleAnimation.destroy();
        avatarIdleAnimation = null;
    }

    avatarSpeakingAnimation = lottie.loadAnimation({
        container: document.getElementById("avatar-container"),
        renderer: "svg",
        loop: true,
        autoplay: true,
        path: "static/animations/talking_et_urso.json" // Ajuste para o seu arquivo "falando"
    });
}

// Função chamada ao clicar no botão de enviar mensagem
function sendMessage() {
    let input = document.getElementById("chat-input");
    let message = input.value.trim();
    if (message) {
        addMessage("Você: " + message, "user");
        input.value = "";

        // Aqui você faz a lógica de envio da mensagem ao servidor
        // Exemplo fictício com fetch POST
        fetch("/send_message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                addMessage("Bot: " + data.response, "bot");

                // Toca o áudio da resposta se disponível
                if (data.audio_url) {
                    playAudioFeedback(data.audio_url);
                }
            })
            .catch(err => console.error(err));
    }
}

// Função chamada ao clicar no botão de gravação
function startRecording() {
    console.log("startRecording function called");
    let button = document.getElementById("record-button");
    button.classList.add("recording");

    // Aqui você faz a lógica de gravação e envia ao servidor
    // Exemplo fictício com fetch POST
    fetch("/record", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            button.classList.remove("recording");
            addMessage("Você: [Gravação finalizada]", "user");
            addMessage("Transcrição: " + data.transcription, "bot");
            addMessage("Feedback: " + data.feedback, "bot");

            // Toca o áudio do feedback
            if (data.audio_url) {
                playAudioFeedback(data.audio_url);
            }
        })
        .catch(err => {
            console.error(err);
            button.classList.remove("recording");
        });
}

// Toca o áudio e controla a animação do avatar
function playAudioFeedback(url) {
    // Muda para animação speaking
    loadAvatarSpeaking();
    isSpeaking = true;

    let audio = new Audio(url);
    audio.play();

    audio.onended = () => {
        // Volta pra idle quando terminar
        loadAvatarIdle();
        isSpeaking = false;
    };
}

// Exibe mensagens no chat
function addMessage(text, sender) {
    let chatBox = document.getElementById("chat-box");
    let msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
