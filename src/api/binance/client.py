import requests         # Libreria para hacer llamadas HTTP (API)
import time             # Para pausar ejecucion y evitar bloqueos de API

BASE_URL = "https://api.binance.com/api/v3/klines"
FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
ORDERBOOK_URL = "https://api.binance.com/api/v3/depth"



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

        response = requests.get(BASE_URL, params=params)            # Peticion GET a Binance
        data = response.json()
        if not data:
            break

        all_data.extend(data)
        start_time = data[-1][0] + 1                                # = UltimaVela[timestamp] + EvitaDuplicados
        print(f"{symbol}: {len(all_data)} registros")               
        time.sleep(0.5)                                             # Espera medio segundo entre requests

        if len(data) < 1000:
            break

    return all_data                                                 # Devuelve TODAS las velas descargadas




def get_funding_rate(symbol, start_time=None, end_time=None):
    all_data = []

    while True:
        params = {
            "symbol": symbol,
            "limit": 1000
        }

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        response = requests.get(FUNDING_URL, params=params)
        data = response.json()
        if not data:
            break

        all_data.extend(data)
        start_time = int(data[-1]["fundingTime"]) + 1
        print(f"{symbol} funding: {len(all_data)} registros")
        time.sleep(0.5)

        if len(data) < 1000:
            break

    return all_data




def get_order_book(symbol, limit=100):
    params = {
        "symbol": symbol,
        "limit": limit  # 5, 10, 20, 50, 100, 500, 1000
    }

    response = requests.get(ORDERBOOK_URL, params=params)
    data = response.json()

    return data