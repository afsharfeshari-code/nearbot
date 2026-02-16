import requests
from tradingview_ta import TA_Handler, Interval

# ====== تنظیمات تلگرام ======
API_TELEGRAM = "8448021675:AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k"
CHAT_ID = "7107618784"

# ====== تنظیمات استراتژی ======
DELTA = 0.001
LEVERAGE = 20
TARGET_MOVE = 0.10 / LEVERAGE   # 0.5% حرکت قیمت → 10% PnL
STOP_MOVE = 0.40 / LEVERAGE     # 2% حرکت قیمت → 40% ضرر با لورج 20

# فقط نماد NEARUSDT
symbol_handler = TA_Handler(
    symbol="NEARUSDT",
    screener="crypto",
    exchange="BINANCE",
    interval=Interval.INTERVAL_5_MINUTES
)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error sending telegram message:", e)

def check_signal():
    try:
        analysis = symbol_handler.get_analysis()
        close = analysis.indicators["close"]
        high = analysis.indicators["high"]
        low = analysis.indicators["low"]

        # هشدارها
        alert_type = None
        if close >= high * (1 + DELTA):
            alert_type = 'above'
        elif close <= low * (1 - DELTA):
            alert_type = 'below'

        if alert_type:
            entry = None
            if alert_type == 'above' and close <= high * (1 - DELTA):
                entry = 'SHORT'
            elif alert_type == 'below' and close >= low * (1 + DELTA):
                entry = 'LONG'

            if entry:
                send_telegram(f"Signal: {entry} on NEARUSDT | Price: {close}")
                print(f"Signal sent: {entry} at {close}")

    except Exception as e:
        print("Error fetching TradingView data:", e)

# ====== اجرای دائمی ======
import time
while True:
    check_signal()
    time.sleep(60)  # هر ۶۰ ثانیه یکبار چک می‌کنه
