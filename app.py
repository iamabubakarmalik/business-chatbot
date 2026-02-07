from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json, uuid, re, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

ai = OpenAI()

CLIENT_FILE = "clients.json"
LEADS_FILE = "leads.json"

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def ai_reply(message, business):
    res = ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a business chatbot.

Industry: {business.get('industry')}
Services: {business.get('services')}
Pricing: {business.get('pricing')}
Tone: {business.get('tone')}

Goal: convert visitors into leads.
"""
            },
            {"role": "user", "content": message}
        ],
        max_tokens=200
    )
    return res.choices[0].message.content.strip()

# ---------------- PAGES ----------------

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

# ---------------- CLIENT ----------------

@app.route("/client/signup", methods=["POST"])
def client_signup():
    data = request.json
    cid = str(uuid.uuid4())[:8]

    clients = load_json(CLIENT_FILE, {})
    clients[cid] = {
        "name": data["name"],
        "email": data["email"],
        "password": data["password"],
        "business": {
            "industry": "",
            "services": "",
            "pricing": "",
            "tone": "professional"
        }
    }

    save_json(CLIENT_FILE, clients)
    return jsonify({"success": True, "client_id": cid})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data["message"]
    client_id = data["client_id"]

    clients = load_json(CLIENT_FILE, {})
    if client_id not in clients:
        return jsonify({"reply": "Invalid client"})

    email = re.search(r"\S+@\S+\.\S+", msg)
    if email:
        leads = load_json(LEADS_FILE, [])
        leads.append({
            "email": email.group(),
            "client_id": client_id
        })
        save_json(LEADS_FILE, leads)
        return jsonify({"reply": "Thanks! We’ll contact you soon 📧"})

    reply = ai_reply(msg, clients[client_id]["business"])
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
