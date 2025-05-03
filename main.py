import requests
import time
from datetime import datetime, timedelta

# Telegram credentials
BOT_TOKEN = "8078513994:AAGPkKjKskHHi6CS60Vcds91zD3TPqdRsHk"
CHAT_ID = "6691656994"
API_KEY = "f08525d9a49041dfaeb3805f8dad7908"

symbols = {
    "Gold": "XAU/USD",
    "US30": "DIA",
    "NASDAQ": "QQQ"
}

last_signal = {name: None for name in symbols}
last_trade_time = {name: datetime.utcnow() - timedelta(minutes=15) for name in symbols}
cooldown = timedelta(minutes=15)  # prevent back-to-back signals

def send_alert(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def fetch_data(symbol):
    try:
        base = "https://api.twelvedata.com"
        ts = f"{base}/time_series?symbol={symbol}&interval=1min&apikey={API_KEY}&outputsize=2"
        rsi = f"{base}/rsi?symbol={symbol}&interval=1min&apikey={API_KEY}"
        ema = f"{base}/ema?symbol={symbol}&interval=1min&time_period=21&apikey={API_KEY}"

        ts_data = requests.get(ts).json()["values"]
        rsi_data = float(requests.get(rsi).json()["values"][0]["rsi"])
        ema_data = float(requests.get(ema).json()["values"][0]["ema"])

        # candle logic
        open1 = float(ts_data[0]["open"])
        close1 = float(ts_data[0]["close"])
        open2 = float(ts_data[1]["open"])
        close2 = float(ts_data[1]["close"])

        candle = {
            "is_bullish": close1 > open1 and open1 < close2 and close1 > open2,
            "is_bearish": close1 < open1 and open1 > close2 and close1 < open2
        }

        return float(ts_data[0]["close"]), rsi_data, ema_data, candle
    except:
        return None, None, None, None

def evaluate_market(name, symbol):
    global last_trade_time

    now = datetime.utcnow()
    if now - last_trade_time[name] < cooldown:
        return

    price, rsi, ema, candle = fetch_data(symbol)
    if not price:
        return

    if rsi < 30 and candle["is_bullish"] and price > ema:
        if last_signal[name] != "BUY":
            last_signal[name] = "BUY"
            last_trade_time[name] = now
            send_alert(f"🔵 BUY signal on {name}\nPrice: {price:.2f}\nRSI: {rsi:.2f} | EMA: {ema:.2f}")
    elif rsi > 70 and candle["is_bearish"] and price < ema:
        if last_signal[name] != "SELL":
            last_signal[name] = "SELL"
            last_trade_time[name] = now
            send_alert(f"🔴 SELL signal on {name}\nPrice: {price:.2f}\nRSI: {rsi:.2f} | EMA: {ema:.2f}")

# Start bot
send_alert("✅ Bot running with optimized small-account entry logic...")

while True:
    for name, symbol in symbols.items():
        evaluate_market(name, symbol)
    time.sleep(60)