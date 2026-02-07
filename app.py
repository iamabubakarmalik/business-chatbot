from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json, uuid, re, os, time
from openai import OpenAI
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# ======================
# ENV
# ======================
load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-secret")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

CLIENT_FILE = "clients.json"
LEADS_FILE = "leads.json"

# ======================
# APP
# ======================
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

CORS(app)

ai_client = OpenAI()

# ======================
# TEMP MEMORY (non-critical)
# ======================
user_memory = {}

# ======================
# HELPERS
# ======================
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def error(msg, code=400):
    return jsonify({"success": False, "error": msg}), code

# ======================
# AI REPLY
# ======================
def ai_reply(message, business):
    try:
        response = ai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are an AI chatbot for a business.

Industry: {business.get('industry', '')}
Services: {business.get('services', '')}
Pricing: {business.get('pricing', '')}
Tone: {business.get('tone', 'professional')}

Be helpful, professional, concise, and convert visitors into leads.
"""
                },
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            timeout=15
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Sorry, I'm having trouble right now. Please try again in a moment."

# ======================
# ADMIN
# ======================
@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if not data:
        return error("Invalid request")

    if data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True, "token": ADMIN_TOKEN})

    return error("Invalid credentials", 401)

@app.route("/admin/clients")
def admin_clients():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return error("Unauthorized", 403)

    return jsonify(load_json(CLIENT_FILE, {}))

@app.route("/admin/add-client", methods=["POST"])
def admin_add_client():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return error("Unauthorized", 403)

    data = request.get_json()
    if not data:
        return error("Invalid data")

    client_id = str(uuid.uuid4())[:8]

    clients = load_json(CLIENT_FILE, {})
    clients[client_id] = {
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "password": generate_password_hash(data.get("password", "")),
        "plan": data.get("plan", "free"),
        "business": {
            "industry": "",
            "services": "",
            "pricing": "",
            "tone": "professional"
        }
    }

    save_json(CLIENT_FILE, clients)
    return jsonify({"success": True, "client_id": client_id})

@app.route("/admin/leads")
def admin_leads():
    if request.headers.get("Authorization") != ADMIN_TOKEN:
        return error("Unauthorized", 403)

    return jsonify(load_json(LEADS_FILE, []))

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

# ======================
# CLIENT
# ======================
@app.route("/client/signup", methods=["POST"])
def client_signup():
    data = request.get_json()
    if not data:
        return error("Invalid request")

    client_id = str(uuid.uuid4())[:8]
    clients = load_json(CLIENT_FILE, {})

    clients[client_id] = {
        "name": data.get("name"),
        "email": data.get("email"),
        "password": generate_password_hash(data.get("password")),
        "plan": "free",
        "business": {
            "industry": "",
            "services": "",
            "pricing": "",
            "tone": "professional"
        }
    }

    save_json(CLIENT_FILE, clients)
    return jsonify({"success": True, "client_id": client_id})

@app.route("/client/login", methods=["POST"])
def client_login():
    data = request.get_json()
    clients = load_json(CLIENT_FILE, {})

    for cid, c in clients.items():
        if c["email"] == data.get("email") and check_password_hash(c["password"], data.get("password")):
            return jsonify({"success": True, "client_id": cid, "name": c["name"]})

    return error("Invalid login", 401)

@app.route("/client/settings", methods=["POST"])
def client_settings():
    data = request.get_json()
    clients = load_json(CLIENT_FILE, {})

    cid = data.get("client_id")
    if cid not in clients:
        return error("Invalid client")

    clients[cid]["business"] = data.get("business", {})
    save_json(CLIENT_FILE, clients)

    return jsonify({"success": True})

@app.route("/client/leads/<client_id>")
def client_leads(client_id):
    if request.headers.get("Client-ID") != client_id:
        return error("Unauthorized", 403)

    leads = load_json(LEADS_FILE, [])
    return jsonify([l for l in leads if l["client_id"] == client_id])

# ======================
# CHATBOT
# ======================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data:
        return error("Invalid request")

    msg = data.get("message", "")
    client_id = data.get("client_id")
    user_id = data.get("user_id", "guest")

    clients = load_json(CLIENT_FILE, {})
    if client_id not in clients:
        return jsonify({"reply": "Invalid client"})

    user_memory.setdefault(user_id, {})

    if "my name is" in msg.lower():
        name = msg.split("is")[-1].strip()
        user_memory[user_id]["name"] = name
        return jsonify({"reply": f"Nice to meet you {name} 😊"})

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", msg)
    if email_match:
        leads = load_json(LEADS_FILE, [])
        leads.append({
            "name": user_memory[user_id].get("name", "Unknown"),
            "email": email_match.group(),
            "client_id": client_id,
            "timestamp": int(time.time())
        })
        save_json(LEADS_FILE, leads)
        return jsonify({"reply": "Thanks! Your email has been saved 📧"})

    business = clients[client_id].get("business", {})
    reply = ai_reply(msg, business)

    if "name" in user_memory[user_id]:
        reply = f"{user_memory[user_id]['name']}, {reply}"

    return jsonify({"reply": reply})

@app.route("/demo")
def demo():
    return render_template("demo.html")

# ======================
# HEALTH + HOME
# ======================
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/")
def home():
    return render_template("index.html")

# ======================
# RUN
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
