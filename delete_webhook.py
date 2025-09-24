from telegram import Bot

bot = Bot("8370234162:AAGIxb5nUkjXwaxAagUr74fwrBdyLXIMlwA")
bot.delete_webhook()
print("Webhook deleted. You can now use get_updates()")
