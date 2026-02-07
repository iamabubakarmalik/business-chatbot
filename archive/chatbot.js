const button = document.getElementById("chatbot-button");
const box = document.getElementById("chatbot-box");
const input = document.getElementById("chatbot-input");
const messages = document.getElementById("chatbot-messages");

const CLIENT_ID = "bb88c1de"; // 👈 apna client_id yahan dalo
const USER_ID = "web-user-" + Math.random().toString(36).slice(2);

button.onclick = () => {
    box.style.display = box.style.display === "none" ? "block" : "none";
};

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
