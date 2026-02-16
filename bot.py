import requests
import time
import datetime
import os

# ========================
# تنظیمات
# ========================

SYMBOL = "NEARUSDT"
DELTA = 0.001
LEVERAGE = 20
TARGET_MOVE = 0.10 / LEVERAGE
STOP_MOVE = 0.40 / LEVERAGE

BOT_TOKEN = os.getenv("8448021675:AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k")
CHAT_ID = os.getenv("7107618784")

BINANCE_URL = "https://api.binance.com/api/v3/klines"

# ========================
# توابع کمکی
# ========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def get_klines(interval, limit=200):
    params = {
        "symbol": SYMBOL,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(BINANCE_URL, params=params)
    return response.json()

def check_alert(close_5m, high_4h, low_4h):
    if close_5m >= high_4h * (1 + DELTA):
        return "above"
    elif close_5m <= low_4h * (1 - DELTA):
        return "below"
    return None

def check_entry(close_5m, high_4h, low_4h, alert_type):
    if alert_type == "above" and close_5m <= high_4h * (1 - DELTA):
        return "SHORT"
    elif alert_type == "below" and close_5m >= low_4h * (1 + DELTA):
        return "LONG"
    return None

# ========================
# منطق اصلی
# ========================

print("Bot Started...")

active_trade = None

while True:
    try:
        klines_4h = get_klines("4h", 2)
        klines_5m = get_klines("5m", 50)
        klines_1m = get_klines("1m", 100)

        high_4h = float(klines_4h[-2][2])
        low_4h = float(klines_4h[-2][3])

        alert_type = None

        # بررسی هشدار در 5 دقیقه
        for k in klines_5m:
            close_5m = float(k[4])
            alert = check_alert(close_5m, high_4h, low_4h)
            if alert:
                alert_type = alert
                break

        # بررسی ورود
        if alert_type and not active_trade:
            for k in klines_5m:
                close_5m = float(k[4])
                entry = check_entry(close_5m, high_4h, low_4h, alert_type)
                if entry:
                    active_trade = {
                        "direction": entry,
                        "entry_price": close_5m
                    }

                    send_telegram(
                        f"📢 SIGNAL {entry}\n"
                        f"Symbol: {SYMBOL}\n"
                        f"Entry: {close_5m}"
                    )
                    break

        # مدیریت معامله با 1 دقیقه
        if active_trade:
            for k in klines_1m:
                high_1m = float(k[2])
                low_1m = float(k[3])

                entry_price = active_trade["entry_price"]
                direction = active_trade["direction"]

                if direction == "LONG":
                    if high_1m >= entry_price * (1 + TARGET_MOVE):
                        send_telegram("✅ TARGET HIT")
                        active_trade = None
                        break
                    elif low_1m <= entry_price * (1 - STOP_MOVE):
                        send_telegram("❌ STOP LOSS HIT")
                        active_trade = None
                        break

                if direction == "SHORT":
                    if low_1m <= entry_price * (1 - TARGET_MOVE):
                        send_telegram("✅ TARGET HIT")
                        active_trade = None
                        break
                    elif high_1m >= entry_price * (1 + STOP_MOVE):
                        send_telegram("❌ STOP LOSS HIT")‌
                        active_trade = None
                        break

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(30)
