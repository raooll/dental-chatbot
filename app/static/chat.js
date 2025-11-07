const chatbox = document.getElementById("chatbox");
const input = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");

// Enable or disable send button dynamically
input.addEventListener("input", () => {
  sendBtn.disabled = input.value.trim() === "";
});

// Send on click or Enter key
sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !sendBtn.disabled) {
    sendMessage();
  }
});

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;

  appendMessage("user", message);
  input.value = "";
  sendBtn.disabled = true;

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    console.log(data)
    appendMessage("bot", data.message);
  } catch (error) {
    appendMessage("bot", "Sorry, there was an error processing your request.");
  }
}

function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.className = `chat ${sender === "user" ? "chat-end" : "chat-start"}`;
  div.innerHTML = `
    <div class="chat-bubble ${
      sender === "user" ? "chat-bubble-primary" : "chat-bubble-info"
    }">${text}</div>
  `;
  chatbox.appendChild(div);
  chatbox.scrollTop = chatbox.scrollHeight;
}
