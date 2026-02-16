import requests
import time
from datetime import datetime
import os

SYMBOL = "NEARUSDT"
DELTA = float(os.getenv("DELTA", 0.001))

API_TELEGRAM = os.getenv("8448021675:AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k")
CHAT_ID = os.getenv("7107618784")

# ==============================
# تلگرام
# ==============================

def send_telegram_message(message):
    if not API_TELEGRAM or not CHAT_ID:
        print("توکن یا چت آیدی تنظیم نشده")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
    except Exception as e:
        print("خطا در ارسال پیام:", e)

# ==============================
# گرفتن کندل‌ها از بایننس
# ==============================

def get_klines(symbol, interval, limit=500):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()

    klines = []
    for k in data:
        klines.append({
            "time": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4])
        })

    return klines

# ==============================
# اجرای ربات
# ==============================

def main():

    send_telegram_message("ربات فعال شد ✅")

    alert_type = None
    alert_candle_index = None
    active_trade = None

    while True:
        try:
            # گرفتن دیتا
            klines_4h = get_klines(SYMBOL, "4h", 10)
            klines_5m = get_klines(SYMBOL, "5m", 500)

            high_4h = max(k["high"] for k in klines_4h[:-1])
            low_4h = min(k["low"] for k in klines_4h[:-1])

            current_index = len(klines_5m) - 2
            last_5m = klines_5m[current_index]
            close_5m = float(last_5m["close"])

            # ==========================
            # 1️⃣ بررسی هشدار
            # ==========================

            if alert_type is None:

                if close_5m > high_4h * (1 + DELTA):
                    alert_type = "BUY"
                    alert_candle_index = current_index
                    send_telegram_message("⚠️ هشدار BUY ثبت شد")

                elif close_5m < low_4h * (1 - DELTA):
                    alert_type = "SELL"
                    alert_candle_index = current_index
                    send_telegram_message("⚠️ هشدار SELL ثبت شد")

            # ==========================
            # 2️⃣ بررسی ورود تا ۴۰ کندل
            # ==========================

            if alert_type and active_trade is None:

                candles_passed = current_index - alert_candle_index

                if candles_passed <= 40:

                    if alert_type == "BUY" and close_5m > high_4h:
                        active_trade = {
                            "type": "BUY",
                            "entry": close_5m
                        }
                        send_telegram_message(f"🚀 ورود BUY در {close_5m}")

                    elif alert_type == "SELL" and close_5m < low_4h:
                        active_trade = {
                            "type": "SELL",
                            "entry": close_5m
                        }
                        send_telegram_message(f"🚀 ورود SELL در {close_5m}")

                else:
                    # بعد از ۴۰ کندل ریست شود
                    alert_type = None
                    alert_candle_index = None

            time.sleep(5)

        except Exception as e:
            print("خطا:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
