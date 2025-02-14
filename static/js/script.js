// Carrega o avatar animado com Lottie
document.addEventListener("DOMContentLoaded", function () {
    lottie.loadAnimation({
        container: document.getElementById("avatar-container"),
        renderer: "svg",
        loop: true,
        autoplay: true,
        path: "static/animations/avatar.json"  // Certifique-se de que o arquivo existe
    });
});

function startRecording() {
    let button = document.getElementById("record-button");
    button.classList.add("recording");

    $.post("/record", function (data) {
        button.classList.remove("recording");

        addMessage("Você: Gravação finalizada", "user");
        addMessage("Transcrição: " + data.transcription, "bot");
        addMessage("Feedback: " + data.feedback, "bot");

        // Toca o áudio do feedback
        if (data.audio_url) {
            let audio = new Audio(data.audio_url);
            audio.play();
        }
    });
}

function addMessage(text, sender) {
    let chatBox = document.getElementById("chat-box");
    let msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
