let recognition;
let isListening = false;

function initVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Voice search is not supported in this browser.");
    return;
  }

  if (!recognition) {
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const input = document.getElementById("q");
      if (input) {
        input.value = transcript;
        document.getElementById("searchForm").submit();
      }
      stopListening();
    };

    recognition.onerror = (event) => {
      console.error("Voice recognition error:", event.error);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
    };
  }

  // Toggle listening state
  if (!isListening) {
    startListening();
  } else {
    stopListening();
  }
}

function startListening() {
  try {
    recognition.start();
    isListening = true;

    // Change button color and icon to show "listening"
    const micBtn = document.getElementById("mic-btn");
    micBtn.style.backgroundColor = "#dc2626"; // red when listening
    micBtn.title = "Stop listening";

    // Play mic start sound
    const startSound = new Audio("/static/sounds/sound1.wav");
    startSound.play().catch(() => {});

    // Show overlay
    showListeningOverlay(true);
  } catch (err) {
    console.error("Error starting recognition:", err);
  }
}

function stopListening() {
  try {
    recognition.stop();
  } catch (err) {
    console.error("Error stopping recognition:", err);
  }

  isListening = false;

  // Reset button
  const micBtn = document.getElementById("mic-btn");
  micBtn.style.backgroundColor = "#334155"; // default gray
  micBtn.title = "Start voice input";

  // Play mic stop sound (optional, same sound)
  const stopSound = new Audio("/static/sounds/sound1.wav");
  stopSound.play().catch(() => {});

  // Remove overlay
  showListeningOverlay(false);
}

function showListeningOverlay(show) {
  let overlay = document.getElementById("listening-overlay");

  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "listening-overlay";
    overlay.textContent = "🎤 Listening...";
    overlay.style.position = "fixed";
    overlay.style.bottom = "180px";
    overlay.style.right = "90px";
    overlay.style.background = "rgba(6,182,212,0.9)";
    overlay.style.color = "white";
    overlay.style.padding = "10px 16px";
    overlay.style.borderRadius = "8px";
    overlay.style.fontSize = "15px";
    overlay.style.fontWeight = "500";
    overlay.style.boxShadow = "0 4px 8px rgba(0,0,0,0.3)";
    overlay.style.transition = "opacity 0.3s ease";
    overlay.style.zIndex = "9999";
    document.body.appendChild(overlay);
  }

  overlay.style.display = show ? "block" : "none";
}
