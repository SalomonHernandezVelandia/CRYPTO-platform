import os
import pandas as pd

from src.api.binance.client import get_historical_data, get_funding_rate
from processing.cleaning.save_raw import save_raw_to_csv, save_funding_to_csv
from src.config.settings import SYMBOLS, INTERVAL, START_DATE



# Saber cuál fue el último dato guardado en el CSV, para asi solo descargar datos nuevos
def get_last_timestamp(file_path, column="open_time"):
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    df[column] = pd.to_datetime(df[column])
    return int(df[column].max().timestamp() * 1000)     # Devuelve el timestamp del último dato guardado 
                                                        # => Busca la fecha MÁS RECIENTE.Convierte la fecha a segundos UNIX. *1000 porque Binance usa milisegundos.



# ========== FUJO PRINCIPAL ===================
def main():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                     # Carpeta raíz del proyecto.

    for symbol in SYMBOLS:
        file_path = os.path.join(base_path, "data", "raw", "binance", f"{symbol}.csv")

        last_timestamp = get_last_timestamp(file_path)                                          # ¿Hasta que fecha esta guardado?
        if last_timestamp:
            start_time = last_timestamp + 1                                                     # SOLO datos nuevos
        else:
            start_time = int(pd.Timestamp(START_DATE).timestamp() * 1000)                       # Si no existe empieza desde la fecha inicial.
        print(f"{symbol} desde: {start_time}")
        data = get_historical_data(symbol, INTERVAL, start_time)                    

        if data:                                                                                # Si Binance devolvió datos: limpia, concatena, elimina duplicados, guarda csv
            save_raw_to_csv(data, symbol, base_path)                                                        
        else:
            print(f"{symbol} ya está actualizado")
        

        # --------------------- FUNDING RATE -----------------------------------------
        funding_symbol = symbol  # mismo nombre BTCUSDT
        funding_file = os.path.join(base_path, "data", "raw", "binance", "funding_rate", f"{symbol}.csv")
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

    # # ===================================================================================
    # # Después de actualizar todo, calcula indicadores, genera señales, envia a Telegram.
    # from jobs.run_signal import run
    # run()



if __name__ == "__main__":
    main()