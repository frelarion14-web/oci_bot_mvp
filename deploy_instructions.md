# تعليمات نشر سريعة (Render / Heroku)

## المتطلبات
- حساب على Render.com أو Heroku.com
- إعداد متغيرات البيئة:
  - TG_TOKEN = توكن البوت من BotFather
  - ADMIN_GROUP_ID = معرف جروب الإدارة (مثل -1001234567890)
  - PORT = 10000 (أو اترك الافتراضي)
  - DB_PATH = مسار قاعدة sqlite (اختياري)

## Render (مبسّط)
1. أنشئ Web Service جديد واختر Docker أو Python.
2. ادفع الكود إلى GitHub واربطه بـ Render.
3. في متغيرات البيئة (Environment) ضع `TG_TOKEN` و `ADMIN_GROUP_ID`.
4. بعد نشر الخدمة، سجل الويب هوك:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<your-render-host>/webhook/<YOUR_TOKEN>
   ```

## Heroku (مبسّط)
1. ارفع المشروع إلى Heroku (git push heroku main).
2. اضف Config Vars (TG_TOKEN, ADMIN_GROUP_ID).
3. شغّل الويب هوك كما في الأعلى.

## الحصول على ADMIN_GROUP_ID
- أبسط طريقة: أضف البوت إلى الجروب، ارسل رسالة في الجروب، ثم نفّذ:
  ```
  https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
  ```
  ابحث عن الرسالة وستجد `chat.id` والذي سيكون هو معرف الجروب (عادة يبدأ بـ -100).
- بدلاً من ذلك استخدم بوتات مثل @getidsbot أو @RawDataBot في تليجرام.

