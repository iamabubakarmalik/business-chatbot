(function () {
  const CLIENT_ID = "demo"; // har client ka alag hoga

  const box = document.createElement("div");
  box.innerHTML = `
    <div style="
      position:fixed;bottom:20px;right:20px;
      width:300px;background:white;
      border:1px solid #ccc;border-radius:10px;
      font-family:Arial;z-index:9999;
    ">
      <div style="background:#333;color:white;padding:10px;">
        🤖 Business Chatbot
      </div>
      <div id="cb-msg" style="height:200px;overflow:auto;padding:10px;"></div>
      <input id="cb-input" style="width:70%;" />
      <button id="cb-send">Send</button>
    </div>
  `;
  document.body.appendChild(box);

  document.getElementById("cb-send").onclick = async () => {
    const input = document.getElementById("cb-input");
    const msg = input.value;
    if (!msg) return;

    const messages = document.getElementById("cb-msg");
    messages.innerHTML += `<div><b>You:</b> ${msg}</div>`;
    input.value = "";

    const res = await fetch("http://127.0.0.1:5000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: msg,
    client_id: CLIENT_ID,
    user_id: "browser_user"
  })
});


    const data = await res.json();
    messages.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
    messages.scrollTop = messages.scrollHeight;
  };
})();
