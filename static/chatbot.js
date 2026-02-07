let clientId = "";

function login() {
    fetch("/client/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            clientId = data.client_id;

            document.getElementById("login").style.display = "none";
            document.getElementById("dashboard").style.display = "block";
            document.getElementById("welcome").innerText =
                "Welcome " + data.name;
        } else {
            document.getElementById("login-msg").innerText =
                "Login failed";
        }
    })
    .catch(err => {
        document.getElementById("login-msg").innerText =
            "Server error";
        console.error(err);
    });
}

function loadLeads() {
    fetch(`/client/leads/${clientId}`, {
        headers: { "Client-ID": clientId }
    })
    .then(res => res.json())
    .then(leads => {
        const ul = document.getElementById("leads");
        ul.innerHTML = "";

        if (leads.length === 0) {
            ul.innerHTML = "<li>No leads yet</li>";
            return;
        }

        leads.forEach(l => {
            const li = document.createElement("li");
            li.innerText = `${l.name} - ${l.email}`;
            ul.appendChild(li);
        });
    });
}
