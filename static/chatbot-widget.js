const CLIENT_ID = "be71a946";   // 🔴 yahan apna client_id
const USER_ID = "browser_user_1";

function addMessage(text, sender) {
    const div = document.createElement("div");
    div.innerText = sender + ": " + text;
    document.getElementById("messages").appendChild(div);
}

async function sendMsg() {
    const input = document.getElementById("msg");
    const message = input.value;
    if (!message) return;

    addMessage(message, "You");
    input.value = "";

    const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message,
            client_id: CLIENT_ID,
            user_id: USER_ID
        })
    });

    const data = await res.json();
    addMessage(data.reply, "Bot");
}
