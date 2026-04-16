import pandas as pd
import os

def save_raw_to_csv(data, symbol, base_path):
    import pandas as pd
    import os

    new_df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    new_df["open_time"] = pd.to_datetime(new_df["open_time"], unit="ms")

    numeric_cols = ["open", "high", "low", "close", "volume"]
    new_df[numeric_cols] = new_df[numeric_cols].astype(float)

    new_df = new_df[["open_time", "open", "high", "low", "close", "volume"]]

    path = os.path.join(base_path, "data", "raw", "binance")
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, f"{symbol}.csv")

    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        old_df["open_time"] = pd.to_datetime(old_df["open_time"])

        df = pd.concat([old_df, new_df])
        df = df.drop_duplicates(subset=["open_time"])
        df = df.sort_values("open_time")
    else:
        df = new_df

    df.to_csv(file_path, index=False)

    print(f"Actualizado: {file_path}")