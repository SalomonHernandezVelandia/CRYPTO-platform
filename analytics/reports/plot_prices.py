import pandas as pd
import matplotlib.pyplot as plt
import os

# 📌 raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT",
    "DOGEUSDT", "ADAUSDT", "LINKUSDT", "XMRUSDT",
    "AVAXUSDT", "HBARUSDT", "SHIBUSDT", "PEPEUSDT"
]

def load_data(symbol):
    file_path = os.path.join(BASE_DIR, "data", "raw", "binance", f"{symbol}.csv")
    return pd.read_csv(file_path)

def prepare_data(df):
    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.sort_values("open_time")
    return df

def plot_all_cryptos():
    fig, axes = plt.subplots(3, 4)  # 3 filas, 4 columnas
    axes = axes.flatten()  # convertir a lista plana

    for i, symbol in enumerate(SYMBOLS):
        try:
            df = load_data(symbol)
            df = prepare_data(df)

            axes[i].plot(df["open_time"], df["close"])
            axes[i].set_title(symbol)
            axes[i].tick_params(axis='x', rotation=45)

        except Exception as e:
            axes[i].set_title(f"{symbol} ERROR")
            print(f"Error con {symbol}: {e}")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_all_cryptos()