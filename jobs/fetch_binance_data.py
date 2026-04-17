import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import pandas as pd

from processing.cleaning.save_raw import save_raw_to_csv, save_funding_to_csv
from exchange_API.binance.client import (
    get_historical_data,
    get_funding_rate
)


SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT",
    "DOGEUSDT", "ADAUSDT", "LINKUSDT", "XMRUSDT",
    "AVAXUSDT", "HBARUSDT", "SHIBUSDT", "PEPEUSDT", "XLMUSDT"
]
INTERVAL = "1h"                     # 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M
START_DATE = "2017-01-01"


def get_last_timestamp(file_path, column="open_time"):
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)
    df[column] = pd.to_datetime(df[column])

    return int(df[column].max().timestamp() * 1000)

def main():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for symbol in SYMBOLS:

        file_path = os.path.join(base_path, "data", "raw", "binance", f"{symbol}.csv")

        last_timestamp = get_last_timestamp(file_path)

        if last_timestamp:
            start_time = last_timestamp + 1   # 🔥 SOLO datos nuevos
        else:
            start_time = int(pd.Timestamp(START_DATE).timestamp() * 1000)

        print(f"{symbol} desde: {start_time}")

        data = get_historical_data(symbol, INTERVAL, start_time)

        if data:
            save_raw_to_csv(data, symbol, base_path)
        else:
            print(f"{symbol} ya está actualizado")

        
        # -------------------------------
        # 🔥 FUNDING RATE
        # -------------------------------
        funding_symbol = symbol  # mismo nombre BTCUSDT

        funding_file = os.path.join(
            base_path, "data", "raw", "binance", "funding_rate", f"{symbol}.csv"
        )

        last_funding_timestamp = get_last_timestamp(funding_file, column="time")

        if last_funding_timestamp:
            funding_start = last_funding_timestamp + 1
        else:
            funding_start = int(pd.Timestamp(START_DATE).timestamp() * 1000)

        funding_data = get_funding_rate(funding_symbol, funding_start)

        if funding_data:
            save_funding_to_csv(funding_data, symbol, base_path)
        else:
            print(f"{symbol} funding actualizado")


if __name__ == "__main__":
    main()