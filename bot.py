import pandas as pd
import ccxt
import time
import requests

# ----------------- تنظیمات -----------------
API_TELEGRAM =8448021675:"AAE0Z4jRdHZKLVXxIBEfpCb9lUbkkxmlW-k"
CHAT_ID = "7107618784"
SYMBOL = "NEAR/USDT"
LEVERAGE = 20
TARGET_MOVE = 0.10 / LEVERAGE
STOP_MOVE = 0.40 / LEVERAGE
DELTA = 0.001
# -----------------------------------------

exchange = ccxt.binance()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{API_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_ohlcv(timeframe):
    data = exchange.fetch_ohlcv(SYMBOL, timeframe=timeframe, limit=100)
    df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

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

def main_loop():
    while True:
        df_4h = get_ohlcv("4h")
        df_5m = get_ohlcv("5m")
        df_1m = get_ohlcv("1m")

        last_4h = df_4h.iloc[-2]
        next_4h_start = df_4h.iloc[-1]['time']
        df_5m_slice = df_5m[df_5m['time'] >= next_4h_start].reset_index(drop=True)

        alert_type = None
        for i, row in df_5m_slice.iterrows():
            alert = check_alert(row, last_4h['high'], last_4h['low'])
            if alert:
                alert_type = alert
                break

        if alert_type:
            for j in range(i+1, len(df_5m_slice)):
                entry_signal = check_entry(df_5m_slice.iloc[j], last_4h['high'], last_4h['low'], alert_type)
                if entry_signal:
                    msg = f"سیگنال {entry_signal} برای {SYMBOL} پیدا شد! قیمت: {df_5m_slice.iloc[j]['close']}"
                    print(msg)
                    send_telegram(msg)
                    break

        time.sleep(60)  # هر دقیقه یک بار چک شود

if name == "main":
    send_telegram("ربات سیگنال NEARUSDT آنلاین شد ✅")
    main_loop()
