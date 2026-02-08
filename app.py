# ===============================
# IMPORTS & SETUP
# ===============================
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

import json
import uuid
import re
import os

load_dotenv()

# ===============================
# APP INITIALIZATION
# ===============================
app = Flask(__name__)
CORS(app)

ai_client = OpenAI()

# ===============================
# FILE PATHS
# ===============================
CLIENT_FILE = "clients.json"
LEADS_FILE = "leads.json"

# ===============================
# UTILITIES
# ===============================
def load_json(path, default):
    """Safely load JSON file"""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    """Save JSON file with formatting"""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ===============================
# AI RESPONSE
# ===============================
def ai_reply(message, business):
    """
    Generate AI response based on client's business configuration
    """
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
You are an AI business chatbot.

Industry: {business.get("industry")}
Services: {business.get("services")}
Pricing: {business.get("pricing")}
Tone: {business.get("tone")}

Goal:
- Answer clearly
- Be professional
- Convert visitors into leads
"""
            },
            {
                "role": "user",
                "content": message
            }
        ],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# ===============================
# PUBLIC PAGES
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/demo")
def demo():
    return render_template("demo.html")


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/client/login", methods=["POST"])
def client_login():
    data = request.json
    clients = load_json(CLIENT_FILE, {})

    for cid, c in clients.items():
        if c["email"] == data["email"] and c["password"] == data["password"]:
            return jsonify({"success": True, "client_id": cid})

    return jsonify({"success": False}), 401

# ===============================
# CLIENT SIGNUP
# ===============================
@app.route("/client/signup", methods=["POST"])
def client_signup():
    data = request.get_json()

    client_id = str(uuid.uuid4())[:8]
    clients = load_json(CLIENT_FILE, {})

    clients[client_id] = {
        "name": data.get("name"),
        "email": data.get("email"),
        "password": data.get("password"),
        "business": {
            "industry": "",
            "services": "",
            "pricing": "",
            "tone": "professional"
        }
    }

    save_json(CLIENT_FILE, clients)

    return jsonify({
        "success": True,
        "client_id": client_id
    })


# ===============================
# CHATBOT API
# ===============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    message = data.get("message", "")
    client_id = data.get("client_id")

    clients = load_json(CLIENT_FILE, {})

    if client_id not in clients:
        return jsonify({"reply": "Invalid client"}), 400

    # ---- Email detection (lead capture)
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", message)
    if email_match:
        leads = load_json(LEADS_FILE, [])
        leads.append({
            "email": email_match.group(),
            "client_id": client_id
        })
        save_json(LEADS_FILE, leads)

        return jsonify({
            "reply": "Thanks! Our team will contact you soon 📧"
        })


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"
ADMIN_TOKEN = "admin-secret"

@app.route("/admin")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    if data["username"] == ADMIN_USERNAME and data["password"] == ADMIN_PASSWORD:
        return jsonify({"success": True, "token": ADMIN_TOKEN})
    return jsonify({"success": False}), 401

@app.route("/admin/clients")
def admin_clients():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(load_json(CLIENT_FILE, {}))

@app.route("/admin/leads")
def admin_leads():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(load_json(LEADS_FILE, []))

    # ---- AI response
    business = clients[client_id]["business"]
    reply = ai_reply(message, business)

    return jsonify({"reply": reply})


# ===============================
# SERVER START
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
