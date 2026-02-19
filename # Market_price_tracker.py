import yfinance as yf
import time
import requests
from datetime import datetime
import pytz

STOCK = "NVDA"  
THRESHOLD = 0.1 
CHECK_INTERVAL = 60  
MARKET_TZ = pytz.timezone("US/Eastern")


TG_TOKEN = "8205563945:AAE7rQHCggCz9WAUKhZ9NnLz6LwIm9QZTx4"
CHAT_ID = "6089451277"

def notify(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def get_price(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m",prepost=True)
    return data["Close"].iloc[-1]

def market_open_now():
    now = datetime.now(tz=MARKET_TZ)
    open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    premarket_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
    afterhours_end = now.replace(hour=20, minute=0, second=0, microsecond=0)
    if now.weekday() >= 5:
        return "closed"
    elif premarket_start <= now < open_time:
        return "premarket"
    elif open_time <= now <= close_time:
        return "open"
    elif close_time < now <= afterhours_end:
        return "afterhours"
    else:
        return "closed"

def main():
    last_price = get_price(STOCK)
    last_state = None
    print(f"Tracking {STOCK}. Starting price: {last_price:.2f}")

    
    
    while True:
        try:
            current_state = market_open_now()

            if last_state is None:
                last_state = current_state

            if current_state != last_state:
                if current_state:
                    print("Market OPENED")
                    notify("Market OPENED")
                    
                else:
                    print("Market CLOSED")
                    notify("Market CLOSED")
                last_state = current_state

            time.sleep(CHECK_INTERVAL)
            price = get_price(STOCK)
            change = ((price - last_price) / last_price) * 100
            if abs(change) >= THRESHOLD:
                direction = "up" if change > 0 else "down"
                msg = f"{STOCK} moved {direction} by {change:.2f}% — current price: ${price:.2f}"
                print(msg)
                notify(msg)
                last_price = price
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
