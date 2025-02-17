let avatarIdleAnimation, avatarSpeakingAnimation;
let isSpeaking = false;  // controle se TTS está em reprodução
let currentModel = 'ollama'; // default model
let isRecording = false;

document.addEventListener("DOMContentLoaded", function () {
    // Carrega o avatar em modo idle
    loadAvatarIdle();

    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
});

function selectModel(model) {
    currentModel = model;
    document.getElementById('ollama-btn').classList.toggle('bg-blue-700', model === 'ollama');
    document.getElementById('openai-btn').classList.toggle('bg-purple-700', model === 'openai');
}

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

        fetch(`/chat/${currentModel}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            addMessage("Bot: " + data.response, "bot");
            if (data.audio_url) {
                loadAvatarSpeaking();
                playAudioFeedback(data.audio_url);
            }
        })
        .catch(err => console.error(err));
    }
}

// Função chamada ao clicar no botão de gravação
function startRecording() {
    const button = document.getElementById('record-button');
    
    if (!isRecording) {
        isRecording = true;
        button.classList.add('recording');
        
        fetch('/record', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: currentModel
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }
            
            // Add transcription to chat
            addMessage("Você: " + data.transcription, "user");
            
            // Add response to chat and play audio
            addMessage("Bot: " + data.response, "bot");
            if (data.audio_url) {
                loadAvatarSpeaking();
                playAudioFeedback(data.audio_url);
            }
        })
        .catch(err => console.error(err))
        .finally(() => {
            isRecording = false;
            button.classList.remove('recording');
        });
    }
}

// Toca o áudio e controla a animação do avatar
function playAudioFeedback(url) {
    const audio = new Audio(url);
    audio.play();
    audio.onended = () => {
        loadAvatarIdle();
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
