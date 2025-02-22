let avatarIdleAnimation, avatarSpeakingAnimation;
let isSpeaking = false;  // controle se TTS está em reprodução
let currentModel = 'ollama'; // default model
let isRecording = false;
let starCount = 0;

document.addEventListener("DOMContentLoaded", function () {
    // Carrega o avatar em modo idle
    loadAvatarIdle();

    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    // Add sound effects for header icons
    const teddyIcon = document.getElementById('teddy-icon');
    const bookIcon = document.getElementById('book-icon');

    teddyIcon.addEventListener('click', () => playSound('static/sounds/boing.mp3'));
    bookIcon.addEventListener('click', () => playSound('static/sounds/ting.mp3'));
});

function selectModel(model) {
    currentModel = model;
    const ollamaBtn = document.getElementById('ollama-btn');
    const openaiBtn = document.getElementById('openai-btn');
    ollamaBtn.classList.toggle('active', model === 'ollama');
    openaiBtn.classList.toggle('active', model === 'openai');
    playSound('static/sounds/click.mp3'); // Sound on model selection
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
        playSound('static/sounds/ding.mp3'); // Play sound on send

        let chatBox = document.getElementById("chat-box");
        let loadingDiv = document.createElement("div");
        loadingDiv.classList.add("loading");
        chatBox.appendChild(loadingDiv);

        fetch(`/chat/${currentModel}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            chatBox.removeChild(loadingDiv);
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
        playSound('static/sounds/stop-recording.mp3'); // Play sound on recording start
        
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
            playSound('static/sounds/stop-recording.mp3'); // Play sound on recording stop
        });
    }
}

// Toca o áudio e controla a animação do avatar
function playAudioFeedback(url) {
    const audio = new Audio(url);
    const speechBubble = document.getElementById('speech-bubble');
    audio.play();
    speechBubble.textContent = "I'm listening..."; // Or dynamic text from the bot
    speechBubble.classList.remove('hidden');
    setTimeout(() => speechBubble.classList.add('hidden'), 3000); // Hide after 3 seconds
    audio.onended = () => {
        loadAvatarIdle();
        playSound('static/sounds/stop-recording.mp3'); // Add a fun sound
    };
}

// Exibe mensagens no chat
function addMessage(text, sender) {
    let chatBox = document.getElementById("chat-box");
    let msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.innerText = text;

    // Add rewards and confetti for user messages
    if (sender === "user") {
        starCount++;
        const rewardCounter = document.getElementById("reward-counter");
        rewardCounter.textContent = `You’ve earned ${starCount} stars today! ⭐`;
        rewardCounter.classList.add('animate-bounce');
        setTimeout(() => rewardCounter.classList.remove('animate-bounce'), 1000);

        // Confetti effect
        for (let i = 0; i < 20; i++) {
            const confetti = document.createElement("div");
            confetti.classList.add("confetti");
            confetti.style.position = "absolute";
            confetti.style.width = "10px";
            confetti.style.height = "10px";
            confetti.style.background = `hsl(${Math.random() * 360}, 70%, 50%)`;
            confetti.style.borderRadius = "50%";
            confetti.style.top = `${Math.random() * 100}%`;
            confetti.style.left = `${Math.random() * 100}%`;
            confetti.style.animation = `fall ${Math.random() * 2 + 1}s linear`;
            chatBox.appendChild(confetti);
            setTimeout(() => confetti.remove(), 3000);
        }
    }

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Play sound function
function playSound(url) {
    const audio = new Audio(url);
    audio.play().catch(err => console.error("Error playing sound:", err));
}