function saveSettings() {
    const client_id = localStorage.getItem("client_id");

    if (!client_id) {
        alert("Please login first");
        return;
    }

    fetch("/client/settings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            client_id: client_id,
            business: {
                industry: document.getElementById("industry").value,
                services: document.getElementById("services").value,
                pricing: document.getElementById("pricing").value,
                tone: document.getElementById("tone").value
            }
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("msg").innerText = "Saved successfully ✅";
    });
}
