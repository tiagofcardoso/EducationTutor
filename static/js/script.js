let avatarIdleAnimation, avatarSpeakingAnimation;
let isSpeaking = false;  // controle se TTS está em reprodução
let currentModel = 'ollama'; // default model
let isRecording = false;
let starCount = 0;
let mediaRecorder;
let audioChunks = [];
let currentAudio = null; // Track the currently playing audio

document.addEventListener("DOMContentLoaded", function () {
    // Carrega o avatar em modo idle
    loadAvatarIdle();

    document.getElementById('chat-input').addEventListener('keypress', function (e) {
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

    isSpeaking = false;
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

    isSpeaking = true;
}

// Função chamada ao clicar no botão de enviar mensagem
function sendMessage() {
    // If audio is currently playing, stop it
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
        // Return to idle animation if we were speaking
        if (isSpeaking) {
            loadAvatarIdle();
        }
    }

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
            body: JSON.stringify({
                message: message,
                voice: "Camila" // Specify which Polly voice to use (can be made configurable)
            })
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
            .catch(err => {
                console.error(err);
                chatBox.removeChild(loadingDiv);
                addMessage("Error: Could not connect to the server. Please try again later.", "error");
            });
    }
}

// Function to get supported MIME type for mobile
function getSupportedMimeType() {
    if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        return 'audio/webm;codecs=opus';
    } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        return 'audio/webm';
    } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        return 'audio/mp4';
    } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
        return 'audio/ogg;codecs=opus';
    } else if (MediaRecorder.isTypeSupported('audio/aac')) {
        return 'audio/aac';
    }
    return null;
}

// Add this new function to check browser compatibility
function checkAudioSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Audio recording is not supported in this browser. Please try using Chrome, Firefox, or Safari.');
    }

    if (!MediaRecorder) {
        throw new Error('MediaRecorder is not supported in this browser. Please try using Chrome, Firefox, or Safari.');
    }

    return true;
}

async function startRecording() {
    // If audio is currently playing, stop it first
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
        // Return to idle animation if we were speaking
        if (isSpeaking) {
            loadAvatarIdle();
        }
    }

    try {
        checkAudioSupport();
        const mimeType = getSupportedMimeType();
        if (!mimeType) {
            throw new Error('No supported audio format found in this browser');
        }

        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                channelCount: 1,
                sampleRate: 44100,
                sampleSize: 16
            }
        });

        mediaRecorder = new MediaRecorder(stream, {
            mimeType: mimeType,
            audioBitsPerSecond: 128000
        });

        audioChunks = [];

        // Update UI
        const recordButton = document.getElementById('record-button');
        recordButton.innerHTML = '<i class="fas fa-stop"></i>';
        recordButton.classList.add('bg-red-500');
        recordButton.onclick = stopRecording;

        addMessage("Recording... Tap the red button to stop.", "system");

        // Auto-send when recording stops
        mediaRecorder.onstop = async () => {
            try {
                const audioBlob = new Blob(audioChunks, { type: mimeType });
                await sendAudioToServer(audioBlob);

                // Reset audio chunks after sending
                audioChunks = [];
            } catch (error) {
                console.error('Error processing audio:', error);
                addMessage("Failed to process audio. Please try again.", "error");
            }
        };

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.start(1000);

    } catch (error) {
        console.error('Recording error:', error);
        let errorMessage = 'Error accessing microphone. ';

        if (error.name === 'NotAllowedError') {
            errorMessage += 'Please allow microphone access to use this feature.';
        } else {
            errorMessage = error.message;
        }

        addMessage(errorMessage, "error");
    }
}

async function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        try {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());

            // Reset UI immediately
            const recordButton = document.getElementById('record-button');
            recordButton.innerHTML = '<i class="fas fa-microphone"></i>';
            recordButton.classList.remove('bg-red-500');
            recordButton.onclick = startRecording;

            // Show processing message
            addMessage("Processing your audio...", "system");
        } catch (error) {
            console.error('Error stopping recording:', error);
            addMessage("Error stopping recording. Please try again.", "error");
        }
    }
}

async function sendAudioToServer(audioBlob) {
    try {
        const formData = new FormData();

        // Use the correct file extension based on MIME type
        const extension = audioBlob.type.includes('webm') ? 'webm' :
            audioBlob.type.includes('mp4') ? 'm4a' :
                audioBlob.type.includes('ogg') ? 'ogg' : 'wav';

        formData.append('audio', audioBlob, `recording.${extension}`);

        // Show processing message
        addMessage("Processing audio...", "system");

        const response = await fetch('/transcribe', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        if (data.text) {
            // Automatically send the transcribed message
            addMessage("Transcribed text: " + data.text, "system");

            // Send to chat system
            let chatBox = document.getElementById("chat-box");
            let loadingDiv = document.createElement("div");
            loadingDiv.classList.add("loading");
            chatBox.appendChild(loadingDiv);

            const chatResponse = await fetch(`/chat/${currentModel}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: data.text,
                    voice: "Camila" // Specify Polly voice to use
                })
            });

            if (!chatResponse.ok) {
                throw new Error(`Chat API error: ${chatResponse.status}`);
            }

            const chatData = await chatResponse.json();
            chatBox.removeChild(loadingDiv);

            if (chatData.response) {
                addMessage("Bot: " + chatData.response, "bot");
                if (chatData.audio_url) {
                    loadAvatarSpeaking();
                    playAudioFeedback(chatData.audio_url);
                }
            }
        } else {
            throw new Error('No transcription received');
        }
    } catch (error) {
        console.error('Error sending audio:', error);
        addMessage(`Error: ${error.message}`, "error");
    }
}

// Toca o áudio e controla a animação do avatar
function playAudioFeedback(url) {
    // First stop any currently playing audio
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }

    // Create new audio instance
    currentAudio = new Audio(url);

    // Switch to speaking animation
    loadAvatarSpeaking();

    // Show speech bubble with visual indicator
    const speechBubble = document.getElementById('speech-bubble');
    if (speechBubble) {
        speechBubble.textContent = "Speaking...";
        speechBubble.classList.remove('hidden');
    }

    // Create audio analyzer for visualizations (optional)
    try {
        // Add visualization if you want to show audio waveform
        // This is optional and can be expanded later
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaElementSource(currentAudio);
        source.connect(analyser);
        analyser.connect(audioContext.destination);
    } catch (e) {
        console.log("Audio visualization not supported in this browser");
    }

    // Play the audio
    currentAudio.play().catch(err => {
        console.error("Error playing audio:", err);
        // If playback fails, switch back to idle animation
        loadAvatarIdle();
    });

    // When audio ends, switch back to idle animation
    currentAudio.onended = () => {
        loadAvatarIdle();
        if (speechBubble) {
            speechBubble.classList.add('hidden');
        }
        playSound('static/sounds/stop-recording.mp3'); // Add a fun sound when done
        currentAudio = null;
    };

    // Add event listener for errors
    currentAudio.onerror = () => {
        console.error("Audio playback error:", currentAudio.error);
        loadAvatarIdle();
        if (speechBubble) {
            speechBubble.classList.add('hidden');
        }
        currentAudio = null;
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
        if (rewardCounter) {
            rewardCounter.textContent = `You've earned ${starCount} stars today! ⭐`;
            rewardCounter.classList.add('animate-bounce');
            setTimeout(() => rewardCounter.classList.remove('animate-bounce'), 1000);
        }

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
    audio.volume = 0.5; // Set volume to 50%
    audio.play().catch(err => console.error("Error playing sound:", err));
}