import os
import json
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# قراءة متغيرات البيئة
TOKEN = os.getenv("TG_TOKEN")
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID"))

bot = Bot(token=TOKEN)
app = Flask(__name__)

# ضبط Dispatcher
dispatcher = Dispatcher(bot, None, workers=0)

# تحميل الأسئلة الشائعة
with open("faqs.json", "r", encoding="utf-8") as f:
    faqs = json.load(f)

# دالة الرد على الرسائل
def handle_message(update, context):
    text = update.message.text.lower()
    reply = faqs.get(text, "شكراً لسؤالك، سيتم تحويل استفسارك للإدارة.")
    
    # إرسال الرد للطالب أو تحويل للجروب إذا غير موجود
    if text not in faqs:
        bot.send_message(chat_id=ADMIN_CHANNEL_ID, text=f"استفسار جديد من @{update.message.from_user.username or 'مجهول'}:\n{text}")
    else:
        update.message.reply_text(reply)

# إضافة Handler
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Webhook endpoint
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# تشغيل محلي
if __name__ == "__main__":
    app.run(port=5000)
