import requests
import time
from datetime import datetime, timedelta

# ===============================
# تنظیمات
# ===============================
SYMBOL = "NEARUSDT"  # دقیقاً همون که گفتی
DELTA = 0.001
LEVERAGE = 20
TARGET_MOVE = 0.10 / LEVERAGE
STOP_MOVE = 0.40 / LEVERAGE

API_TELEGRAM = "8448021675:AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k"
CHAT_ID = "7107618784"

# ===============================
# توابع کمکی
# ===============================
def send_telegram_message(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
    except Exception as e:
        print("خطا در ارسال پیام تلگرام:", e)

def get_klines(symbol, interval="5m", limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        data = requests.get(url, timeout=10).json()
    except Exception as e:
        print("خطا در گرفتن دیتا:", e)
        return []

    klines = []
    for d in data:
        try:
            klines.append({
                "time": datetime.fromtimestamp(d[0]/1000),
                "open": float(d[1]),
                "high": float(d[2]),
                "low": float(d[3]),
                "close": float(d[4])
            })
        except:
            continue
    return klines

def check_alert(candle, high_4h, low_4h):
    if candle['close'] >= high_4h * (1 + DELTA):
        return 'above'
    elif candle['close'] <= low_4h * (1 - DELTA):
        return 'below'
    return None

def check_entry(candle, high_4h, low_4h, alert_type):
    if alert_type == 'above' and candle['close'] <= high_4h * (1 - DELTA):
        return 'SHORT'
    elif alert_type == 'below' and candle['close'] >= low_4h * (1 + DELTA):
        return 'LONG'
    return None

def open_trade(direction, price, start_time):
    return {"direction": direction, "entry_price": price, "start_time": start_time, "status": "open"}

# ===============================
# حلقه اصلی
# ===============================
def main():
    send_telegram_message("ربات فعال شد ✅")

    alert_type = None
    alert_index = None
    alert_end_time = None
    active_trade = None

    while True:
        try:
            klines_4h = get_klines(SYMBOL, "4h", 10)
            klines_5m = get_klines(SYMBOL, "5m", 500)
            klines_1m = get_klines(SYMBOL, "1m", 500)

            if len(klines_4h) < 2 or len(klines_5m) < 50:
                print("دیتا کافی نیست")
                time.sleep(5)
                continue

            high_4h = max(k["high"] for k in klines_4h[:-1])
            low_4h = min(k["low"] for k in klines_4h[:-1])
            current_index = len(klines_5m) - 2
            last_5m = klines_5m[current_index]
            current_time = last_5m["time"]

            # ==========================
            # 1️⃣ ثبت هشدار
            # ==========================
            if alert_type is None:
                alert = check_alert(last_5m, high_4h, low_4h)
                if alert:
                    alert_end_time = klines_4h[-1]["time"]
                    if alert_end_time - current_time <= timedelta(minutes=30):
                        print("⚠️ هشدار ثبت نشد، کمتر از 30 دقیقه تا پایان کندل 4h")
                    else:
                        alert_type = alert
                        alert_index = current_index
                        send_telegram_message(f"⚠️ هشدار {alert} ثبت شد در {current_time}")

            # ==========================
            # 2️⃣ بررسی انقضای هشدار
            # ==========================
            if alert_type and active_trade is None:
                if current_time >= alert_end_time:
                    print("⚠️ هشدار منقضی شد (پایان کندل 4h رسید)")
                    alert_type = None
                    alert_index = None
                    alert_end_time = None

            # ==========================
            # 3️⃣ بررسی ورود
            # ==========================
            if alert_type and active_trade is None:
                for i in range(alert_index + 1, len(klines_5m)):
                    candle = klines_5m[i]
                    entry = check_entry(candle, high_4h, low_4h, alert_type)
                    if entry:
                        if alert_end_time - candle["time"] <= timedelta(minutes=20):
                            print("⚠️ ورود لغو شد، کمتر از 20 دقیقه تا پایان کندل 4h")
                            alert_type = None
                            alert_index = None
                            alert_end_time = None
                            break
                        active_trade = open_trade(entry, candle["close"], candle["time"])
                        send_telegram_message(f"🚀 معامله {entry} باز شد در {candle['close']}")
                        break

            # ==========================
            # 4️⃣ بررسی TP و SL روی 1m
            # ==========================
            if active_trade:
                for candle in klines_1m:
                    if candle["time"] < active_trade["start_time"]:
                        continue

                    trade_closed = False
                    if active_trade['direction'] == "LONG":
                        if candle['high'] >= active_trade['entry_price']*(1 + TARGET_MOVE):
                            pnl = LEVERAGE * TARGET_MOVE
                            active_trade.update({"exit_price": active_trade['entry_price']*(1 + TARGET_MOVE),
                                                 "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                            trade_closed = True
                        elif candle['low'] <= active_trade['entry_price']*(1 - STOP_MOVE):
                            pnl = -LEVERAGE * STOP_MOVE
                            active_trade.update({"exit_price": active_trade['entry_price']*(1 - STOP_MOVE),
                                                 "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                            trade_closed = True

                    elif active_trade['direction'] == "SHORT":
                        if candle['low'] <= active_trade['entry_price']*(1 - TARGET_MOVE):
                            pnl = LEVERAGE * TARGET_MOVE
                            active_trade.update({"exit_price": active_trade['entry_price']*(1 - TARGET_MOVE),
                                                 "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                            trade_closed = True
                        elif candle['high'] >= active_trade['entry_price']*(1 + STOP_MOVE):
                            pnl = -LEVERAGE * STOP_MOVE
                            active_trade.update({"exit_price": active_trade['entry_price']*(1 + STOP_MOVE),
                                                 "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                            trade_closed = True

                    if trade_closed:
                        send_telegram_message(f"✅ معامله بسته شد\nEntry: {active_trade['entry_price']}\nExit: {active_trade['exit_price']}\nPnL: {active_trade['pnl']}")
                        active_trade = None
                        alert_type = None
                        alert_index = None
                        alert_end_time = None
                        break

            time.sleep(5)

        except Exception as e:
            print("خطا اصلی:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
