import pandas as pd
import os

def save_raw_to_csv(data, symbol, base_path):
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df = df[["open_time", "open", "high", "low", "close", "volume"]]

    path = os.path.join(base_path, "data", "raw", "binance")
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, f"{symbol}.csv")

    df.to_csv(file_path, index=False)

    print(f"Guardado en: {file_path}")