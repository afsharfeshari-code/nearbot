import requests
import time
from datetime import datetime

# ---------- تنظیمات ربات ----------
API_TELEGRAM = "8448021675:AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k"
CHAT_ID ="7107618784"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print("خطا در ارسال پیام تلگرام:", e)

# ---------- تنظیمات استراتژی ----------
LEVERAGE = 20              # عدد حتما int باشد
DELTA = 0.001              # عدد حتما float باشد
TARGET_MOVE = 0.10 / LEVERAGE
STOP_MOVE   = 0.40 / LEVERAGE

# ---------- نمونه حلقه اصلی ----------
def main():
    send_telegram_message("ربات وصل شد ✅")
    
    active_trade = None
    alert_type = None
    alert_time = None

    while True:
        try:
            # اینجا فرضی: گرفتن قیمت از API یا هر منبع دلخواه
            price = 1.2345  # مثال
            # اینجا می‌توانی منطق هشدار و ورود/خروج را قرار بدهی

            # تست ساده: اگر قیمت از 1.23 بالاتر رفت هشدار بده
            if price > 1.23 and alert_type is None:
                alert_type = "above"
                alert_time = datetime.now()
                send_telegram_message(f"هشدار بالا ثبت شد ⚠️ در {alert_time}")

            time.sleep(30)

        except Exception as e:
            print("خطا:", e)
            time.sleep(30)

# این خط برای اجرای مستقیم old_bot.py کافی است
if __name__ == "__main__":
    main()
