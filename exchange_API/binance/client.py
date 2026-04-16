import requests         # Libreria para hacer llamadas HTTP (API)
import time             # Para pausar ejecucion y evitar bloqueos de API

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

