(function () {
  const scriptTag = document.currentScript;
  const CLIENT_ID = scriptTag.getAttribute("data-client-id");

  if (!CLIENT_ID) {
    console.error("Chatbot: client_id missing");
    return;
  }

  /* ---------- Styles (isolated) ---------- */
  const style = document.createElement("style");
  style.innerHTML = `
    #cb-bubble {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 56px;
      height: 56px;
      background: #4f46e5;
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      cursor: pointer;
      z-index: 999999;
      box-shadow: 0 8px 20px rgba(0,0,0,.3);
    }

    #cb-box {
      position: fixed;
      bottom: 90px;
      right: 20px;
      width: 320px;
      height: 420px;
      background: #fff;
      border-radius: 12px;
      display: none;
      flex-direction: column;
      overflow: hidden;
      z-index: 999999;
      box-shadow: 0 20px 40px rgba(0,0,0,.3);
      font-family: Arial, sans-serif;
    }

    #cb-header {
      background: #4f46e5;
      color: white;
      padding: 12px;
      font-weight: bold;
    }

    #cb-messages {
      flex: 1;
      padding: 10px;
      overflow-y: auto;
      font-size: 14px;
    }

    #cb-input {
      display: flex;
      border-top: 1px solid #eee;
    }

    #cb-input input {
      flex: 1;
      border: none;
      padding: 10px;
      font-size: 14px;
      outline: none;
    }

    #cb-input button {
      background: #4f46e5;
      color: white;
      border: none;
      padding: 0 16px;
      cursor: pointer;
    }
  `;
  document.head.appendChild(style);

  /* ---------- Bubble ---------- */
  const bubble = document.createElement("div");
  bubble.id = "cb-bubble";
  bubble.innerHTML = "💬";
  document.body.appendChild(bubble);

  /* ---------- Chat Box ---------- */
  const box = document.createElement("div");
  box.id = "cb-box";
  box.innerHTML = `
    <div id="cb-header">AI Assistant</div>
    <div id="cb-messages"></div>
    <div id="cb-input">
      <input placeholder="Type your message..." />
      <button>Send</button>
    </div>
  `;
  document.body.appendChild(box);

  bubble.onclick = () => {
    box.style.display = box.style.display === "none" ? "flex" : "none";
  };

  const input = box.querySelector("input");
  const button = box.querySelector("button");
  const messages = box.querySelector("#cb-messages");

  function add(role, text) {
    const div = document.createElement("div");
    div.style.marginBottom = "8px";
    div.innerHTML = `<b>${role}:</b> ${text}`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  button.onclick = send;
  input.addEventListener("keypress", e => e.key === "Enter" && send());

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";

    add("You", text);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          client_id: CLIENT_ID,
          user_id: "web-" + Math.random().toString(36).slice(2)
        })
      });

      const data = await res.json();
      add("Bot", data.reply);
    } catch {
      add("Bot", "Something went wrong. Please try again.");
    }
  }
})();
