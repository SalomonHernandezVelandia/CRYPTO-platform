import pandas as pd
import matplotlib.pyplot as plt
import os

# 📌 raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_data(symbol):
    file_path = os.path.join(BASE_DIR, "data", "raw", "binance", f"{symbol}.csv")
    return pd.read_csv(file_path)

def plot_price(df, symbol):
    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.sort_values("open_time")

    plt.figure()
    plt.plot(df["open_time"], df["close"])

    plt.title(f"{symbol} Precio")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df = load_data("BTCUSDT")
    plot_price(df, "BTCUSDT")