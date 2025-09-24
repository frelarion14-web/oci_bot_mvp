from telegram import Bot

bot = Bot("8370234162:AAGIxb5nUkjXwaxAagUr74fwrBdyLXIMlwA")
updates = bot.get_updates()  # سيجلب آخر الرسائل

for u in updates:
    if u.channel_post:  # لو القناة أرسلت رسالة
        print("Channel ID:", u.channel_post.chat.id)
