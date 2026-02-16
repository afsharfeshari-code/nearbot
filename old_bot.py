import requests
import time
from datetime import datetime
import os

# ---------- تنظیمات ربات ----------
API_TELEGRAM="8448021675:AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k"
CHAT_ID="7107618784"

def send_telegram_message(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
    except Exception as e:
        print("خطا در ارسال پیام تلگرام:", e)

# ---------- تنظیمات استراتژی ----------
def get_float_env(var_name, default):
    """مطمئن می‌شویم Environment Variable حتما float یا int شود"""
    val = os.getenv(var_name, default)
    try:
        return float(val)
    except:
        return float(default)

LEVERAGE = int(get_float_env("LEVERAGE", 20))   # همیشه int
DELTA    = get_float_env("DELTA", 0.001)        # همیشه float
TARGET_MOVE = 0.10 / LEVERAGE
STOP_MOVE   = 0.40 / LEVERAGE

# ---------- حلقه اصلی ----------
def main():
    send_telegram_message("ربات وصل شد ✅")
    
    active_trade = None
    alert_type = None
    alert_time = None

    while True:
        try:
            # مثال گرفتن قیمت از CSV یا API
            candle_close = 1.2345
            candle_high  = 1.2350
            candle_low   = 1.2330

            # اطمینان از float بودن
            candle_close = float(candle_close)
            candle_high  = float(candle_high)
            candle_low   = float(candle_low)

            # منطق هشدار ساده
            if candle_close > 1.23 and alert_type is None:
                alert_type = "above"
                alert_time = datetime.now()
                send_telegram_message(f"هشدار بالا ثبت شد ⚠️ در {alert_time}")

            time.sleep(30)

        except Exception as e:
            print("خطا:", e)
            time.sleep(30)

# اجرای مستقیم old_bot.py
if __name__ == "__main__":
    main()
