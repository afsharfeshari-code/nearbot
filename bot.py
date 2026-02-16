import time
import requests
from datetime import datetime, timedelta
from binance.client import Client

# ---------- تنظیمات تلگرام ----------
API_TELEGRAM = "8448021675:AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k"
CHAT_ID = "7107618784"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("خطا در ارسال پیام تلگرام:", e)

# ---------- ارسال پیام تست ----------
send_telegram_message("ربات وصل شد ✅")

# ---------- تنظیمات استراتژی ----------
DELTA = 0.001
LEVERAGE = 20
TARGET_MOVE = 0.10 / LEVERAGE   # 0.5% حرکت قیمت → 10% PnL
STOP_MOVE = 0.40 / LEVERAGE     # 2% حرکت قیمت → 40% ضرر با لورج 20

SYMBOL = "NEARUSDT"
INTERVAL_1M = "1m"
INTERVAL_5M = "5m"
INTERVAL_4H = "4h"

# ---------- کلاینت Binance ----------
client = Client()  # فقط public data میخوایم، API key نیاز نیست

# ---------- توابع کمکی ----------
def get_klines(symbol, interval, limit=100):
    """ دریافت کندل‌های اخیر """
    data = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    klines = []
    for d in data:
        klines.append({
            "time": datetime.fromtimestamp(d[0]/1000),
            "open": float(d[1]),
            "high": float(d[2]),
            "low": float(d[3]),
            "close": float(d[4])
        })
    return klines

def check_alert(candle_5m, high_4h, low_4h):
    if candle_5m['close'] >= high_4h * (1 + DELTA):
        return 'above'
    elif candle_5m['close'] <= low_4h * (1 - DELTA):
        return 'below'
    return None

def check_entry(candle_5m, high_4h, low_4h, alert_type):
    if alert_type == 'above' and candle_5m['close'] <= high_4h * (1 - DELTA):
        return 'SHORT'
    elif alert_type == 'below' and candle_5m['close'] >= low_4h * (1 + DELTA):
        return 'LONG'
    return None

def open_trade(direction, price, start_time):
    return {"direction": direction, "entry_price": price, "start_time": start_time, "status": "open"}

# ---------- حلقه اصلی ----------
active_trade = None
alert_type = None
alert_time = None

while True:
    try:
        # گرفتن آخرین کندل‌ها
        klines_4h = get_klines(SYMBOL, INTERVAL_4H, limit=2)
        klines_5m = get_klines(SYMBOL, INTERVAL_5M, limit=20)
        klines_1m = get_klines(SYMBOL, INTERVAL_1M, limit=20)

        high_4h = klines_4h[-2]['high']
        low_4h = klines_4h[-2]['low']

        # پیدا کردن هشدار جدید
        if alert_type is None:
            for candle in klines_5m:
                alert = check_alert(candle, high_4h, low_4h)
                if alert:
                    alert_type = alert
                    alert_time = candle['time']
                    send_telegram_message(f"هشدار {alert} روی کندل 5 دقیقه‌ای در {alert_time} ثبت شد ⚠️")
                    break

        # پیدا کردن کندل ورود
        if alert_type and active_trade is None:
            for candle in klines_5m:
                if candle['time'] < alert_time:
                    continue
                entry = check_entry(candle, high_4h, low_4h, alert_type)
                if entry:
                    active_trade = open_trade(entry, candle['close'], candle['time'])
                    send_telegram_message(f"معامله جدید {entry} باز شد 🔔\nEntry: {candle['close']} Time: {candle['time']}")
                    break

        # بررسی ۱ دقیقه‌ای بعد از ورود
        if active_trade:
            for candle in klines_1m:
                if candle['time'] < active_trade['start_time']:
                    continue

                price_high = candle['high']
                price_low = candle['low']
                trade_closed = False

                if active_trade['direction'] == "LONG":
                    if price_high >= active_trade['entry_price']*(1 + TARGET_MOVE):
                        pnl = LEVERAGE * TARGET_MOVE
                        active_trade.update({"exit_price": active_trade['entry_price']*(1 + TARGET_MOVE),
                                             "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                        trade_closed = True
                    elif price_low <= active_trade['entry_price']*(1 - STOP_MOVE):
                        pnl = -LEVERAGE * STOP_MOVE
                        active_trade.update({"exit_price": active_trade['entry_price']*(1 - STOP_MOVE),
                                             "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                        trade_closed = True

                elif active_trade['direction'] == "SHORT":
                    if price_low <= active_trade['entry_price']*(1 - TARGET_MOVE):
                        pnl = LEVERAGE * TARGET_MOVE
                        active_trade.update({"exit_price": active_trade['entry_price']*(1 - TARGET_MOVE),
                                             "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                        trade_closed = True
                    elif price_high >= active_trade['entry_price']*(1 + STOP_MOVE):
                        pnl = -LEVERAGE * STOP_MOVE
                        active_trade.update({"exit_price": active_trade['entry_price']*(1 + STOP_MOVE),
                                             "pnl": pnl, "status": "closed", "exit_time": candle['time']})
                        trade_closed = True

                if trade_closed:
                    send_telegram_message(f"معامله بسته شد ✅\nDirection: {active_trade['direction']}\nEntry: {active_trade['entry_price']}\nExit: {active_trade['exit_price']}\nPnL: {active_trade['pnl']}")
                    active_trade = None
                    alert_type = None
                    break

        # هر ۳۰ ثانیه چک می‌کنه
        time.sleep(30)

    except Exception as e:
        print("خطا:", e)
        time.sleep(30)
