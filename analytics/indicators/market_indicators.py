import numpy as np

def add_indicators(df):
    # -------------------------------
    # VOLUMEN
    # -------------------------------
    df["vol_ma_20"] = df["volume"].rolling(20).mean()

    # -------------------------------
    # WAP
    # -------------------------------
    df["cum_vol"] = df["volume"].cumsum()
    df["cum_vol_price"] = (df["close"] * df["volume"]).cumsum()
    df["vwap"] = df["cum_vol_price"] / df["cum_vol"]

    # -------------------------------
    # Medias móviles
    # -------------------------------
    df["ma_20"] = df["close"].rolling(20).mean()
    df["ma_50"] = df["close"].rolling(50).mean()

    # -------------------------------
    # Tendencia
    # -------------------------------
    df["trend"] = np.where(df["ma_20"] > df["ma_50"], "Bullish", "Bearish")

    # -------------------------------
    # Volatilidad y rango
    # -------------------------------
    df["volatility"] = df["close"].rolling(20).std()
    df["range"] = df["high"].rolling(20).max() - df["low"].rolling(20).min()

    return df