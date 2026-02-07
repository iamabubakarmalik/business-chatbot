let ADMIN_TOKEN = "";

async function login() {
    const res = await fetch("http://127.0.0.1:5000/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value
        })
    });

    if (!res.ok) {
        alert("Login failed");
        return;
    }

    const data = await res.json();
    ADMIN_TOKEN = data.token;

    document.getElementById("login").style.display = "none";
    document.getElementById("dashboard").style.display = "block";

    loadLeads();
}

async function loadLeads() {
    const res = await fetch("http://127.0.0.1:5000/admin/leads", {
        headers: {
            "Authorization": ADMIN_TOKEN
        }
    });

    const leads = await res.json();
    const tbody = document.getElementById("leads");
    tbody.innerHTML = "";

    leads.forEach(l => {
        const row = `<tr>
            <td>${l.name}</td>
            <td>${l.email}</td>
            <td>${l.client_id}</td>
        </tr>`;
        tbody.innerHTML += row;
    });
}
