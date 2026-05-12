import pandas as pd
import os

def save_raw_to_csv(data, symbol, base_path):
    new_df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    new_df["open_time"] = pd.to_datetime(new_df["open_time"], unit="ms")                        # Convertir fecha: Binance manda timestamps en milisegundos "1712345678000"

    numeric_cols = ["open", "high", "low", "close", "volume", "num_trades", "taker_buy_base"]   # Convertir a float
    new_df[numeric_cols] = new_df[numeric_cols].astype(float)
    new_df = new_df[["open_time", "open", "high", "low", "close", "volume", "num_trades", "taker_buy_base"]]    # Solo se dejan estas columnas

    path = os.path.join(base_path, "data", "raw", "binance")                                    # Crear ruta donde se guardaran los archivos
    os.makedirs(path, exist_ok=True)                                                            # Crea carpeta si no existe
    file_path = os.path.join(path, f"{symbol}.csv")                                             # Crea el nombre del csv

    # Si el csv ya existe se hace lo siguiente...
    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        old_df["open_time"] = pd.to_datetime(old_df["open_time"])           # Convierte fechas otra vez
        df = pd.concat([old_df, new_df])                                    # Une datos nuevos con viejos
        df = df.drop_duplicates(subset=["open_time"])                       # Elimina duplicados ya que Binance puede devolver velas repetidas
        df = df.sort_values("open_time")                                    # Ordena por fechas para mantener el historico limpio.
    else:
        df = new_df                                                         # Si el archivo no existe solo usa los datos nuevos

    df.to_csv(file_path, index=False)                                       # Guarda el archivo
    print(f"Actualizado: {file_path}")



def save_funding_to_csv(data, symbol, base_path):
    df = pd.DataFrame(data)                                                                 # Crea dataframe para los datos de funding
    df["fundingTime"] = pd.to_datetime(df["fundingTime"], unit="ms")                        # Convierte timestamp a fecha.
    df["fundingRate"] = df["fundingRate"].astype(float)                                     # Convertir a float

    df = df[["fundingTime", "fundingRate"]]                                                 # Columnas que se van a conservar
    df = df.rename(columns={"fundingTime": "time"})                                         # Renombrar esa columna

    path = os.path.join(base_path, "data", "raw", "binance", "funding_rate")                # Ruta donde se guardaran los datos
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{symbol}.csv")

    # Si el csv ya existe se hace lo siguiente...
    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        # Detecta archivos antiguos corruptos.
        if "time" not in old_df.columns:
            print(f"⚠️ Archivo viejo detectado en {symbol}, regenerando...")
            old_df = pd.DataFrame(columns=["time", "fundingRate"])
        else:
            old_df["time"] = pd.to_datetime(old_df["time"])

        df = pd.concat([old_df, df])
        df = df.drop_duplicates(subset=["time"])
        df = df.sort_values("time")

    df.to_csv(file_path, index=False)
    print(f"Funding actualizado: {file_path}")