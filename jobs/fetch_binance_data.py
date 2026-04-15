import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import pandas as pd

from exchange_API.binance.client import get_historical_data
from processing.cleaning.save_raw import save_raw_to_csv

SYMBOLS = ["BTCUSDT"]
INTERVAL = "1d"
START_DATE = "2017-01-01"

def main():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    start_time = int(pd.Timestamp(START_DATE).timestamp() * 1000)

    for symbol in SYMBOLS:
        data = get_historical_data(symbol, INTERVAL, start_time)
        save_raw_to_csv(data, symbol, base_path)

if __name__ == "__main__":
    main()