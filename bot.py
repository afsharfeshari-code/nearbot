# bot.py
import requests

# --- تنظیمات تلگرام ---
API_TELEGRAM = "AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k"
CHAT_ID = "7107618784"

# --- تابع ارسال پیام ---
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("پیام با موفقیت ارسال شد ✅")
        else:
            print(f"خطا در ارسال پیام: {response.status_code} - {response.text}")
    except Exception as e:
        print("خطای شبکه:", e)

# --- تست اولیه ---
if __name__ == "__main__":
    send_telegram("سلام! ربات تلگرام تست شد 🟢")
