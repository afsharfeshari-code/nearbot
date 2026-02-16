from flask import Flask
import threading

app = Flask(__name__)

# ---------- وب سرور برای هیت پینگ ----------
@app.route("/")
def home():
    return "OK", 200

# ---------- اجرای ربات در پس‌زمینه ----------
def run_bot():
    import old_bot  # نام فایل رباتت بدون .py
    old_bot.main()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
