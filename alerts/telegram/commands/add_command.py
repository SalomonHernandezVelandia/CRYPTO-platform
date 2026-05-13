import pandas as pd

from src.api.telegram.client import send_message
from src.api.binance.client import get_crypto_price, get_historical_price

from data.portfolio.manager import add_position


def handle_add_command(chat_id, text):
    try:
        parts = text.split()
        user = parts[1].upper()
        symbol = parts[2].upper()
        usdt = float(parts[3])

        # FECHA OPCIONAL
        if len(parts) >= 5:                                         # Para permitir: /add SALOMON BTCUSDT 500 2026-04-01 15:00
            entry_date = pd.to_datetime(" ".join(parts[4:]))        
            entry_date = entry_date + pd.Timedelta(hours=5)         # Convertir hora Colombia -> UTC Binance
            entry_date = entry_date.strftime("%Y-%m-%d %H:%M:%S")
            price = get_historical_price(
                symbol,
                entry_date
            )
        else:
            entry_date = None
            price = get_crypto_price(symbol)

        amount = add_position(                                      # Guarda trade.
            user=user,
            symbol=symbol,
            usdt_invested=usdt,
            entry_price=price,
            entry_date=entry_date
        )

        message_text = (                                            # Mensaje de confirmacion de Trade guardado
            f"✅ Trade agregado correctamente\n\n"
            f"👤 Usuario: {user}\n"
            f"🪙 Symbol: {symbol}\n"
            f"💵 Inversión: {usdt:.2f} USDT\n"
            f"📈 Entry: {price:.4f}\n"
            f"🧮 Coins: {amount:.6f}"
        )
        print(message_text)
        send_message(chat_id, message_text)

    except Exception as e:
        message_text = f"❌ Error ADD:\n{e}"
        print(message_text)
        send_message(chat_id, message_text)