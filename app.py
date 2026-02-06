from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import uuid
import re
import os
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

# ======================
# OPENAI
# ======================
ai_client = OpenAI()

def ai_reply(message, business_name):
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
You are an AI chatbot for a business named {business_name}.
You help website visitors, answer questions, collect leads.
Be polite, professional, and concise.
"""
            },
            {"role": "user", "content": message}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# ======================
# ADMIN
# ======================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"
ADMIN_TOKEN = "admin-secret"

# ======================
# APP
# ======================
app = Flask(__name__)
CORS(app)

# ======================
# MEMORY
# ======================
user_memory = {}

# ======================
# FILES
# ======================
CLIENT_FILE = "clients.json"
LEADS_FILE = "leads.json"

# ======================
# HELPERS
# ======================
def load_clients():
    try:
        with open(CLIENT_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_clients(data):
    with open(CLIENT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_leads():
    try:
        with open(LEADS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_leads(data):
    with open(LEADS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ======================
# ADMIN ROUTES
# ======================
@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True, "token": ADMIN_TOKEN})
    return jsonify({"success": False}), 401

@app.route("/admin/clients")
def admin_clients():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(load_clients())

@app.route("/admin/add-client", methods=["POST"])
def add_client():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    client_id = str(uuid.uuid4())[:8]

    clients = load_clients()
    clients[client_id] = {
        "name": data.get("name"),
        "email": data.get("email"),
        "password": data.get("password"),
        "plan": data.get("plan", "free")
    }

    save_clients(clients)
    return jsonify({"client_id": client_id})

@app.route("/admin/leads")
def admin_leads():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(load_leads())

# ======================
# CLIENT
# ======================
@app.route("/client/login", methods=["POST"])
def client_login():
    data = request.get_json()
    clients = load_clients()

    for cid, client in clients.items():
        if client["email"] == data.get("email") and client["password"] == data.get("password"):
            return jsonify({
                "success": True,
                "client_id": cid,
                "name": client["name"]
            })

    return jsonify({"success": False}), 401

@app.route("/client/leads/<client_id>")
def client_leads(client_id):
    if request.headers.get("Client-ID") != client_id:
        return jsonify({"error": "Unauthorized"}), 403

    leads = load_leads()
    return jsonify([l for l in leads if l["client_id"] == client_id])

@app.route("/client")
def client_dashboard():
    return render_template("client_dashboard.html")

# ======================
# CHATBOT
# ======================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "")
    client_id = data.get("client_id")
    user_id = data.get("user_id", "guest")

    clients = load_clients()
    if client_id not in clients:
        return jsonify({"reply": "Invalid client"})

    if user_id not in user_memory:
        user_memory[user_id] = {}

    msg_lower = msg.lower()

    # Name detection
    if "my name is" in msg_lower:
        name = msg.split("is")[-1].strip()
        user_memory[user_id]["name"] = name
        return jsonify({"reply": f"Nice to meet you {name} 😊"})

    # Email detection
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", msg)
    if email_match:
        email = email_match.group()
        leads = load_leads()
        leads.append({
            "name": user_memory[user_id].get("name", "Unknown"),
            "email": email,
            "client_id": client_id
        })
        save_leads(leads)
        return jsonify({"reply": "Thanks! Your email has been saved 📧"})

    # AI reply
    business_name = clients[client_id]["name"]
    reply = ai_reply(msg, business_name)

    name = user_memory[user_id].get("name")
    if name:
        reply = f"{name}, {reply}"

    return jsonify({"reply": reply})

# ======================
# HOME
# ======================
@app.route("/")
def home():
    return render_template("test.html")

# ======================
# RUN
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
