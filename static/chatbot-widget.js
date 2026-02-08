(function () {
  const scriptTag = document.currentScript;
  const CLIENT_ID = scriptTag.getAttribute("data-client-id");

  if (!CLIENT_ID) {
    console.error("Chatbot: client_id missing");
    return;
  }

  /* ------------------ STYLE ------------------ */
  const style = document.createElement("style");
  style.innerHTML = `
    :root {
      --bg-main: #0B132B;
      --bg-card: #111936;
      --border-soft: #1E2A5A;
      --brand-primary: #3FA9F5;
      --brand-accent: #5EE6FF;
      --text-heading: #FFFFFF;
      --text-body: #B6C2E2;
    }

    #orve-bubble {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 60px;
      height: 60px;
      background: linear-gradient(135deg, #3FA9F5, #5EE6FF);
      color: #0B132B;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      cursor: pointer;
      z-index: 999999;
      box-shadow: 0 0 20px rgba(94,230,255,0.4);
      transition: 0.3s;
    }

    #orve-bubble:hover {
      transform: scale(1.05);
      box-shadow: 0 0 30px rgba(94,230,255,0.6);
    }

    #orve-box {
      position: fixed;
      bottom: 95px;
      right: 20px;
      width: 340px;
      height: 480px;
      background: var(--bg-card);
      border-radius: 16px;
      display: none;
      flex-direction: column;
      overflow: hidden;
      z-index: 999999;
      box-shadow: 0 20px 60px rgba(0,0,0,0.6);
      font-family: Inter, Arial, sans-serif;
      border: 1px solid var(--border-soft);
    }

    #orve-header {
      background: linear-gradient(180deg, #0B132B, #111936);
      color: white;
      padding: 14px;
      font-weight: 600;
      border-bottom: 1px solid var(--border-soft);
    }

    #orve-header small {
      display: block;
      font-size: 11px;
      opacity: 0.6;
    }

    #orve-messages {
      flex: 1;
      padding: 14px;
      overflow-y: auto;
      font-size: 14px;
      color: var(--text-body);
    }

    .orve-msg {
      margin-bottom: 10px;
      max-width: 80%;
      padding: 8px 12px;
      border-radius: 10px;
      line-height: 1.4;
    }

    .orve-user {
      background: var(--brand-primary);
      color: #0B132B;
      margin-left: auto;
    }

    .orve-bot {
      background: #0B132B;
      border: 1px solid var(--border-soft);
    }

    #orve-input {
      display: flex;
      border-top: 1px solid var(--border-soft);
      background: #0B132B;
    }

    #orve-input input {
      flex: 1;
      border: none;
      padding: 12px;
      background: transparent;
      color: white;
      font-size: 14px;
      outline: none;
    }

    #orve-input button {
      background: var(--brand-primary);
      color: #0B132B;
      border: none;
      padding: 0 18px;
      cursor: pointer;
      font-weight: bold;
      transition: 0.2s;
    }

    #orve-input button:hover {
      background: var(--brand-accent);
    }

    /* MOBILE */
    @media (max-width: 480px) {
      #orve-box {
        width: calc(100% - 20px);
        right: 10px;
        bottom: 80px;
        height: 70vh;
      }
    }
  `;
  document.head.appendChild(style);

  /* ------------------ BUBBLE ------------------ */
  const bubble = document.createElement("div");
  bubble.id = "orve-bubble";
  bubble.innerHTML = "🤖";
  document.body.appendChild(bubble);

  /* ------------------ BOX ------------------ */
  const box = document.createElement("div");
  box.id = "orve-box";
  box.innerHTML = `
    <div id="orve-header">
      OrveChat
      <small>An ORVE Solutions Product</small>
    </div>
    <div id="orve-messages"></div>
    <div id="orve-input">
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
  const messages = box.querySelector("#orve-messages");

  function add(role, text) {
    const div = document.createElement("div");
    div.className = "orve-msg " + (role === "user" ? "orve-user" : "orve-bot");
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  button.onclick = send;
  input.addEventListener("keypress", e => e.key === "Enter" && send());

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";

    add("user", text);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          client_id: CLIENT_ID
        })
      });

      const data = await res.json();
      add("bot", data.reply);
    } catch {
      add("bot", "Connection error. Please try again.");
    }
  }
})();
