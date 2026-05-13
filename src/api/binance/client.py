import requests         # Libreria para hacer llamadas HTTP (API)
import pandas as pd
import time             # Para pausar ejecucion y evitar bloqueos de API

BASE_URL = "https://api.binance.com/api/v3/klines"
FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
ORDERBOOK_URL = "https://api.binance.com/api/v3/depth"
PRICE_URL = "https://api.binance.com/api/v3/ticker/price"




# Obtiene precio ACTUAL desde Binance.
def get_crypto_price(symbol):
    url = f"{PRICE_URL}?symbol={symbol}"
    response = requests.get(url).json()

    return float(response["price"])         # Convierte string → número.




# Obtener el precio histórico de entrada.
def get_historical_price(symbol, date_string):
    params = {                                              # Pide vela de 1h, una sola vela
        "symbol": symbol,
        "interval": "1h",
        "limit": 1
    }
    dt = pd.to_datetime(date_string)                        # Convertir fecha a timestamp
    timestamp = int(dt.timestamp() * 1000)                  # Binance usa milisegundos UNIX.
    params["startTime"] = timestamp                         # dame la vela desde este momento.

    response = requests.get(BASE_URL, params=params).json()

    close_price = float(response[0][4])                     # Close price

    return close_price





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