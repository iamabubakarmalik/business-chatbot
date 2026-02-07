document.addEventListener("DOMContentLoaded", function () {
  const config = window.CHATBOT_CONFIG;

  if (!config || !config.client_id || !config.api_url) {
    console.error("❌ Chatbot config missing");
    return;
  }

  // Button
  const btn = document.createElement("div");
  btn.id = "cb-btn";
  btn.innerText = "💬";
  document.body.appendChild(btn);

  // Box
  const box = document.createElement("div");
  box.id = "cb-box";
  box.innerHTML = `
    <div id="cb-header">Chat with us</div>
    <div id="cb-messages"></div>
    <input id="cb-input" placeholder="Type message..." />
  `;
  document.body.appendChild(box);

  const messages = box.querySelector("#cb-messages");
  const input = box.querySelector("#cb-input");
  const user_id = "web-" + Math.random().toString(36).slice(2);

  btn.onclick = () => {
    box.style.display = box.style.display === "flex" ? "none" : "flex";
  };

  input.addEventListener("keypress", async (e) => {
    if (e.key !== "Enter" || !input.value.trim()) return;

    const text = input.value;
    input.value = "";
    messages.innerHTML += `<div class="me">${text}</div>`;

    const res = await fetch(config.api_url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        client_id: config.client_id,
        user_id
      })
    });

    const data = await res.json();
    messages.innerHTML += `<div class="bot">${data.reply}</div>`;
    messages.scrollTop = messages.scrollHeight;
  });

  console.log("✅ Chatbot loaded");
});
