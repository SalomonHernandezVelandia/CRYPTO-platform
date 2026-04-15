import requests
import time

BASE_URL = "https://api.binance.com/api/v3/klines"

def get_historical_data(symbol, interval, start_time, end_time=None):
    all_data = []

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "limit": 1000
        }

        if end_time:
            params["endTime"] = end_time

        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if not data:
            break

        all_data.extend(data)
        start_time = data[-1][0] + 1

        print(f"{symbol}: {len(all_data)} registros")

        time.sleep(0.5)

        if len(data) < 1000:
            break

    return all_data