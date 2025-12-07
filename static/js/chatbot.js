document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("chatbot-toggle");
  const windowEl = document.getElementById("chatbot-window");
  const sendBtn = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-input");
  const messages = document.getElementById("chatbot-messages");

  // Helper: append messages to the chat window
  function appendMessage(text, sender) {
    const div = document.createElement("div");
    div.className = "message " + sender;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  // Handle sending user messages
  function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    input.value = "";

    fetch("/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    })
      .then((r) => r.json())
      .then((data) => {
        appendMessage(data.reply, "bot");
      })
      .catch((err) => {
        appendMessage("Error: could not connect to the server.", "bot");
        console.error(err);
      });
  }

  // ✅ Open/close chatbot and auto-greet when opened
  toggle.addEventListener("click", () => {
    const isActive = windowEl.classList.toggle("active");
    if (isActive) {
      messages.innerHTML = ""; // Clear old messages
      appendMessage("👋 Hi! I'm your HireHub Assistant. How can I help you today?", "bot");
    }
  });
  
  // Close button functionality
const closeBtn = document.getElementById("chatbot-close");
if (closeBtn) {
  closeBtn.addEventListener("click", () => {
    windowEl.classList.remove("active");
  });
}

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });
});
