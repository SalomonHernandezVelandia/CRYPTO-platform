import numpy as np


def add_indicators(df):
    # -------------------------------
    # VOLUMEN
    # -------------------------------
    df["vol_ma_20"] = df["volume"].rolling(20).mean()                           # .rolling(20) Crea una ventana móvil de 20 filas, cuando llega a la vela 20 calcula el promedio de las últimas 20

    # -------------------------------
    # WAP
    # -------------------------------
    df["cum_vol"] = df["volume"].cumsum()                                       # Calcula una Suma acumulativa.
    df["cum_vol_price"] = (df["close"] * df["volume"]).cumsum()                 # Esto calcula: precio × volumen, porque VWAP pondera por volumen.
    df["vwap"] = df["cum_vol_price"] / df["cum_vol"]                            # El precio promedio REAL pagado por el mercado.

    # -------------------------------
    # EMAs (NUEVO SISTEMA)
    # -------------------------------
    df["ema_13"] = df["close"].ewm(span=13, adjust=False).mean()                # El span calcula las ultimas 13 velas (en rango de 15minutos seria = 3h 15m)
    df["ema_48"] = df["close"].ewm(span=48, adjust=False).mean()                # ewn() da mas peso a las velas recientes. 48 velas = 12 horas
    df["ema_200"] = df["close"].ewm(span=200, adjust=False).mean()              # 200 velas = 50 horas

    # -------------------------------
    # Tendencia estructural
    # -------------------------------
    df["trend"] = np.where(df["ema_48"] > df["ema_200"], "Bullish", "Bearish")  # Si EMA 48 > EMA 200 entonces Bullish, de lo contrario Bearish
    # -------------------------------
    # Momentum
    df["momentum"] = np.where(df["ema_13"] > df["ema_48"], "Bullish", "Bearish") # Mide Fuerza de corto plazo.

    # -------------------------------
    # Volatilidad y rango
    # -------------------------------
    df["volatility"] = df["close"].rolling(20).std()                            # Calcula desviación estándar, Qué tanto se mueve el precio. Alta Volatilidad = Velas enormes.
    df["range"] = df["high"].rolling(20).max() - df["low"].rolling(20).min()    # Para detectar consolidadciones, explosiones, mercadpos laterales y comprension.

    return df