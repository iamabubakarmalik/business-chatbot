(function () {
  // ===============================
  // CONFIG
  // ===============================
  const scriptTag = document.currentScript;
  const CLIENT_ID = scriptTag.getAttribute("data-client-id");
  const API_URL = scriptTag.getAttribute("data-api-url") || "/chat";

  if (!CLIENT_ID) {
    console.error("❌ Chatbot: CLIENT_ID missing");
    return;
  }

  const USER_ID =
    "web-" + Math.random().toString(36).substring(2, 10);

  // ===============================
  // LOAD CSS
  // ===============================
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = scriptTag.src.replace(
    "chatbot-widget.js",
    "chatbot-widget.css"
  );
  document.head.appendChild(css);

  // ===============================
  // HTML
  // ===============================
  const bubble = document.createElement("div");
  bubble.id = "cb-bubble";
  bubble.innerHTML = "💬";

  const box = document.createElement("div");
  box.id = "cb-box";
  box.innerHTML = `
    <div id="cb-header">Chat with us</div>
    <div id="cb-messages"></div>
    <input id="cb-input" placeholder="Type your message..." />
  `;

  document.body.appendChild(bubble);
  document.body.appendChild(box);

  // ===============================
  // TOGGLE
  // ===============================
  bubble.onclick = () => {
    box.style.display =
      box.style.display === "flex" ? "none" : "flex";
  };

  // ===============================
  // CHAT
  // ===============================
  const input = box.querySelector("#cb-input");
  const messages = box.querySelector("#cb-messages");

  input.addEventListener("keypress", async (e) => {
    if (e.key !== "Enter") return;

    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    messages.innerHTML += `<div class="cb-user">${text}</div>`;
    messages.scrollTop = messages.scrollHeight;

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          client_id: CLIENT_ID,
          user_id: USER_ID,
        }),
      });

      const data = await res.json();
      messages.innerHTML += `<div class="cb-bot">${data.reply}</div>`;
      messages.scrollTop = messages.scrollHeight;
    } catch (err) {
      messages.innerHTML += `<div class="cb-bot">⚠️ Server error</div>`;
    }
  });
})();
