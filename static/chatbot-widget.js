(function () {
const CLIENT_ID = "bb88c1de";
const USER_ID = "web-" + Math.random().toString(36).slice(2);

  const bubble = document.createElement("div");
  bubble.innerText = "💬";
  bubble.style.cssText = `
    position:fixed;bottom:20px;right:20px;
    width:60px;height:60px;border-radius:50%;
    background:#4f46e5;color:white;
    display:flex;align-items:center;justify-content:center;
    cursor:pointer;z-index:9999;font-size:26px;
  `;
  document.body.appendChild(bubble);

  const box = document.createElement("div");
  box.style.cssText = `
    position:fixed;bottom:90px;right:20px;
    width:320px;height:420px;
    background:white;border-radius:10px;
    box-shadow:0 10px 30px rgba(0,0,0,.2);
    display:none;flex-direction:column;
    z-index:9999;
  `;

  box.innerHTML = `
    <div style="padding:10px;background:#4f46e5;color:white">
      AI Chatbot
    </div>
    <div id="cb-msg" style="flex:1;padding:10px;overflow:auto"></div>
    <input id="cb-input" placeholder="Type message..."
      style="border:none;border-top:1px solid #ddd;padding:10px" />
  `;

  document.body.appendChild(box);

  bubble.onclick = () => {
    box.style.display = box.style.display === "none" ? "flex" : "none";
  };

  const input = box.querySelector("#cb-input");
  const messages = box.querySelector("#cb-msg");

  input.addEventListener("keypress", async (e) => {
    if (e.key === "Enter") {
      const text = input.value;
      input.value = "";
      messages.innerHTML += `<div><b>You:</b> ${text}</div>`;

      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          client_id: CLIENT_ID,
          user_id: USER_ID
        })
      });

      const data = await res.json();
      messages.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
      messages.scrollTop = messages.scrollHeight;
    }
  });
})();
