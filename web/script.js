async function sendMessage() {
  const input = document.getElementById("input");
  const messages = document.getElementById("messages");

  const userMsg = input.value.trim();
  if (!userMsg) return;

  messages.innerHTML += `<div class="user">${userMsg}</div>`;
  input.value = "";

  try {
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMsg })
    });

    const data = await response.json();
    messages.innerHTML += `<div class="bot">${data.reply}</div>`;
    messages.scrollTop = messages.scrollHeight;

  } catch (error) {
    messages.innerHTML += `<div class="bot">⚠️ Server error</div>`;
  }
}
