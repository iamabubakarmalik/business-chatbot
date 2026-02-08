let ADMIN_TOKEN = "";

function login() {
  fetch("/admin/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      username: document.getElementById("username").value,
      password: document.getElementById("password").value
    })
  })
  .then(r => r.json())
  .then(d => {
    if (!d.success) {
      msg.innerText = "Invalid login";
      return;
    }

    ADMIN_TOKEN = d.token;
    window.location.href = "/admin/dashboard";
  });
}

function loadAdminData() {
  loadClients();
  loadLeads();
}

function loadClients() {
  fetch("/admin/clients", {
    headers: {"Authorization": ADMIN_TOKEN}
  })
  .then(r => r.json())
  .then(data => {
    const tbody = document.getElementById("clients");
    tbody.innerHTML = "";

    Object.entries(data).forEach(([id, c]) => {
      tbody.innerHTML += `
        <tr>
          <td>${id}</td>
          <td>${c.name}</td>
          <td>${c.email}</td>
          <td>${c.plan || "free"}</td>
        </tr>
      `;
    });
  });
}

function loadLeads() {
  fetch("/admin/leads", {
    headers: {"Authorization": ADMIN_TOKEN}
  })
  .then(r => r.json())
  .then(leads => {
    const tbody = document.getElementById("leads");
    tbody.innerHTML = "";

    leads.forEach(l => {
      tbody.innerHTML += `
        <tr>
          <td>${l.email}</td>
          <td>${l.client_id}</td>
        </tr>
      `;
    });
  });
}
