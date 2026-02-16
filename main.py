from flask import Flask
import threading

app = Flask(__name__)

# ---------- وب سرور برای هیت پینگ ----------
@app.route("/")
def home():
    return "OK", 200

# ---------- اجرای ربات در پس‌زمینه ----------
def run_bot():
    import old_bot  # اسم فایل رباتت بدون .py
    # اگر old_bot.py تابع main دارد، این خط را فعال کن:
    # old_bot.main()

if __name__ == "__main__":
    # اجرای ربات در یک ترد جداگانه
    threading.Thread(target=run_bot).start()
    
    # اجرای وب سرور Flask روی پورت 8080
    app.run(host="0.0.0.0", port=8080)
