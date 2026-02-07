let clientId = localStorage.getItem("client_id");

function login() {
  fetch("/client/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      email: email.value,
      password: password.value
    })
  })
  .then(r => r.json())
  .then(d => {
    if (!d.success) {
      msg.innerText = "Invalid login";
      return;
    }
    localStorage.setItem("client_id", d.client_id);
    location.href = "/client";
  });
}

function logout() {
  localStorage.removeItem("client_id");
  location.href = "/login";
}

if (clientId && location.pathname === "/client") {
  document.getElementById("welcome").innerText =
    "Welcome 👋 Client ID: " + clientId;

  document.getElementById("embed").innerText =
`<script>
window.CHATBOT_CLIENT_ID = "${clientId}";
</script>
<script src="https://YOUR-DOMAIN/static/chatbot-widget.js"></script>`;

  loadLeads();
}

function saveSettings() {
  fetch("/client/settings", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      client_id: clientId,
      business: {
        industry: industry.value,
        services: services.value,
        pricing: pricing.value,
        tone: tone.value
      }
    })
  })
  .then(r => r.json())
  .then(() => {
    document.getElementById("save-msg").innerText = "Saved ✅";
  });
}

function loadLeads() {
  fetch(`/client/leads/${clientId}`, {
    headers: {"Client-ID": clientId}
  })
  .then(r => r.json())
  .then(data => {
    const ul = document.getElementById("leads");
    ul.innerHTML = "";
    if (!data.length) {
      ul.innerHTML = "<li>No leads yet</li>";
      return;
    }
    data.forEach(l => {
      ul.innerHTML += `<li>${l.name} – ${l.email}</li>`;
    });
  });
}

function signup() {
  fetch("/client/signup", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      name: name.value,
      email: email.value,
      password: password.value
    })
  })
  .then(r => r.json())
  .then(d => {
    if (!d.success) {
      msg.innerText = d.message;
      return;
    }

    localStorage.setItem("client_id", d.client_id);
    location.href = "/client";
  });
}
