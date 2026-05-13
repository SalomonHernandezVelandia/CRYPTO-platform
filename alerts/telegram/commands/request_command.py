import os
import pandas as pd

from src.api.telegram.client import send_message
from src.api.binance.client import get_historical_data, get_funding_rate

from jobs.run_signal import process_symbol
from jobs.fetch_binance_data import get_last_timestamp

from processing.cleaning.save_raw import save_raw_to_csv, save_funding_to_csv




def handle_request_command(chat_id, text):
    parts = text.split()

    # VALIDAR COMANDO
    if len(parts) != 2:
        send_message(
            chat_id,
            "Uso correcto:\n/request BTCUSDT"
        )
        return
    symbol = parts[1].upper()

    try:
        send_message(
            chat_id,
            f"📥 Descargando datos de {symbol}..."
        )
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # KLINES
        file_path = os.path.join(
            base_path,
            "data",
            "raw",
            "binance",
            f"{symbol}.csv"
        )

        last_timestamp = get_last_timestamp(file_path)
        if last_timestamp:
            start_time = last_timestamp + 1
        else:
            start_time = int(pd.Timestamp("2017-01-01").timestamp() * 1000)

        # DESCARGAR KLINES NUEVOS
        data = get_historical_data(symbol, "15m", start_time)

        if data:
            save_raw_to_csv(data,symbol,base_path)

        # DESCARGAR FUNDING NUEVO
        funding_file = os.path.join(
            base_path,
            "data",
            "raw",
            "binance",
            "funding_rate",
            f"{symbol}.csv"
        )

        last_funding_timestamp = get_last_timestamp(funding_file, column="time")
        if last_funding_timestamp:
            funding_start = last_funding_timestamp + 1
        else:
            funding_start = int(pd.Timestamp("2017-01-01").timestamp() * 1000)

        funding_data = get_funding_rate(symbol,funding_start)
        if funding_data:
            save_funding_to_csv(funding_data,symbol,base_path)

        send_message(chat_id, f"📊 Analizando {symbol}...")

        process_symbol(symbol,force_send=True)          # ANALIZAR Y ENVIAR

    except Exception as e:
        message_text = f"❌ Error en request:\n{e}"
        print(message_text)
        send_message(chat_id, message_text)