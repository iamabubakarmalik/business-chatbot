# =====================================
# IMPORTS & CONFIG
# =====================================
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

import json
import uuid
import re
import os

load_dotenv()

# =====================================
# APP INIT
# =====================================
app = Flask(__name__)
CORS(app)

ai = OpenAI()

# =====================================
# FILES
# =====================================
CLIENT_FILE = "clients.json"
LEADS_FILE = "leads.json"
USAGE_FILE = "usage.json"

# =====================================
# PLANS
# =====================================
PLAN_LIMITS = {
    "free": 50,
    "starter": 500,
    "pro": 5000
}

# =====================================
# HELPERS
# =====================================
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------- USAGE ----------
def increment_usage(client_id):
    usage = load_json(USAGE_FILE, {})

    if client_id not in usage:
        usage[client_id] = {"messages": 0}

    usage[client_id]["messages"] += 1
    save_json(USAGE_FILE, usage)

    return usage[client_id]["messages"]

# =====================================
# AI RESPONSE
# =====================================
def ai_reply(message, business):
    response = ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a professional business chatbot.

Industry: {business.get("industry")}
Services: {business.get("services")}
Pricing: {business.get("pricing")}
Tone: {business.get("tone")}

Goal:
- Help visitors
- Be concise
- Collect leads
"""
            },
            {"role": "user", "content": message}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# =====================================
# PUBLIC PAGES
# =====================================
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

# =====================================
# CLIENT AUTH
# =====================================
@app.route("/client/signup", methods=["POST"])
def client_signup():
    data = request.json
    cid = str(uuid.uuid4())[:8]

    clients = load_json(CLIENT_FILE, {})
    clients[cid] = {
        "name": data["name"],
        "email": data["email"],
        "password": data["password"],
        "plan": "free",
        "business": {
            "industry": "",
            "services": "",
            "pricing": "",
            "tone": "professional"
        }
    }

    save_json(CLIENT_FILE, clients)
    return jsonify({"success": True, "client_id": cid})

@app.route("/client/login", methods=["POST"])
def client_login():
    data = request.json
    clients = load_json(CLIENT_FILE, {})

    for cid, c in clients.items():
        if c["email"] == data["email"] and c["password"] == data["password"]:
            return jsonify({"success": True, "client_id": cid})

    return jsonify({"success": False}), 401

# =====================================
# CHATBOT API (⭐ MAIN ⭐)
# =====================================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    client_id = data.get("client_id")

    clients = load_json(CLIENT_FILE, {})
    if client_id not in clients:
        return jsonify({"reply": "Invalid client"})

    client = clients[client_id]
    plan = client.get("plan", "free")
    limit = PLAN_LIMITS.get(plan, 50)

    used = increment_usage(client_id)
    if used > limit:
        return jsonify({
            "reply": "⚠️ Message limit reached. Please upgrade your plan."
        })

    # Lead capture
    email = re.search(r"\S+@\S+\.\S+", message)
    if email:
        leads = load_json(LEADS_FILE, [])
        leads.append({
            "email": email.group(),
            "client_id": client_id
        })
        save_json(LEADS_FILE, leads)
        return jsonify({"reply": "Thanks! We’ll contact you soon 📧"})

    reply = ai_reply(message, client["business"])
    return jsonify({"reply": reply})

# =====================================
# ADMIN (BASIC)
# =====================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"
ADMIN_TOKEN = "admin-secret"

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    if data["username"] == ADMIN_USERNAME and data["password"] == ADMIN_PASSWORD:
        return jsonify({"token": ADMIN_TOKEN})
    return jsonify({"error": "Invalid"}), 401

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

@app.route("/admin/usage")
def admin_usage():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(load_json(USAGE_FILE, {}))

# =====================================
# RUN
# =====================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
