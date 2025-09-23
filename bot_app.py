import os
import sqlite3
from flask import Flask, request, jsonify
import requests
import json

# Load environment vars (or set them in the environment)
TELEGRAM_TOKEN = os.environ.get("TG_TOKEN", "")
BOT_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_GROUP_ID = int(os.environ.get("ADMIN_GROUP_ID", "-1000000000000"))  # ضع رقم الجروب هنا بعد الحصول عليه
DB_PATH = os.environ.get("DB_PATH", "bot.db")
FAQ_FILE = os.environ.get("FAQ_FILE", "faqs.json")

app = Flask(__name__)

# --- Database helpers ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        trigger_keywords TEXT,
        response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        telegram_user_id INTEGER,
        username TEXT,
        message TEXT,
        is_handled INTEGER DEFAULT 0,
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS staff_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        staff_username TEXT,
        reply_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def insert_conversation(telegram_user_id, username, text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (telegram_user_id, username, message) VALUES (?,?,?)", (telegram_user_id, username, text))
    conv_id = c.lastrowid
    conn.commit()
    conn.close()
    return conv_id

def mark_handled(conv_id, staff_username, reply_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE conversations SET is_handled=1, assigned_to=? WHERE id=?", (staff_username, conv_id))
    c.execute("INSERT INTO staff_replies (conversation_id, staff_username, reply_text) VALUES (?,?,?)", (conv_id, staff_username, reply_text))
    conn.commit()
    conn.close()

def load_faqs():
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def send_message(chat_id, text):
    requests.post(f"{BOT_API}/sendMessage", json={"chat_id": chat_id, "text": text})

# Initialize DB & FAQs on start
init_db()
FAQS = load_faqs()

def match_faq(text):
    text_lower = text.lower()
    for faq in FAQS:
        keys = [k.strip() for k in faq.get("trigger_keywords","").split(",") if k.strip()]
        for k in keys:
            if k and k in text_lower:
                return faq.get("response")
    return None

@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"ok": False, "error": "no data"}), 400

    # Handle incoming messages
    if "message" in data:
        msg = data["message"]
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        text = msg.get("text", "") or ""
        user = msg.get("from", {})
        username = user.get("username") or f"{user.get('first_name','')} {user.get('last_name','') or ''}".strip()
        # If message comes from admin group and is a reply command: parse it
        if chat_id == ADMIN_GROUP_ID:
            # expected format: #reply <conv_id>: your reply here
            if text.startswith("#reply"):
                try:
                    # remove prefix
                    parts = text.split(None, 1)
                    if len(parts) > 1:
                        rest = parts[1].strip()
                        # conv_id could be like "12: reply text" or "12 reply text"
                        conv_id_str, reply_text = None, None
                        if ":" in rest:
                            conv_id_str, reply_text = rest.split(":",1)
                        else:
                            p = rest.split(None,1)
                            conv_id_str = p[0]
                            reply_text = p[1] if len(p) > 1 else ""
                        conv_id = int(conv_id_str.strip())
                        reply_text = reply_text.strip()
                        # fetch conversation to get telegram_user_id
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("SELECT telegram_user_id FROM conversations WHERE id=?", (conv_id,))
                        row = c.fetchone()
                        conn.close()
                        if row:
                            telegram_user_id = row[0]
                            # send message to user
                            send_message(telegram_user_id, reply_text)
                            # mark handled
                            mark_handled(conv_id, username, reply_text)
                            send_message(ADMIN_GROUP_ID, f"✅ تم إرسال الرد للمستخدم (conv {conv_id}).")
                        else:
                            send_message(ADMIN_GROUP_ID, "لم أجد محادثة بهذا الرقم.")
                except Exception as e:
                    send_message(ADMIN_GROUP_ID, f"خطأ في معالجة الرد: {e}")
            return jsonify({"ok": True})

        # else: regular user's message
        # Try matching FAQ
        response = match_faq(text)
        if response:
            send_message(chat_id, response)
        else:
            # store conversation and forward to admin group
            conv_id = insert_conversation(chat_id, username, text)
            send_message(chat_id, "تم تحويل سؤالك لفريق المعهد وسيتم الرد عليك قريبًا. حفظك الرب.")
            send_message(ADMIN_GROUP_ID, f"📥 استفسار جديد ({conv_id}) من {username} ({chat_id}):\n{text}")
    return jsonify({"ok": True})

if __name__ == '__main__':
    # Run local dev server
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
