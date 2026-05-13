from src.api.telegram.client import send_message
from src.api.binance.client import get_crypto_price

from data.portfolio.manager import sell_position



def handle_sell_command(chat_id, text):
    try:
        parts = text.split()
        user = parts[1].upper()
        symbol = parts[2].upper()
        price = get_crypto_price(symbol)
        result = sell_position(                                 # Calcula:pnl, dias de trade 
            user=user,
            symbol=symbol,
            exit_price=price
        )

        if result is None:
            message_text = "❌ No existe posición activa"
            print(message_text)
            send_message(chat_id, message_text)
        else:
            message_text = (                                    # Mensaje de confirmacion de Trade guardado
                f"✅ Trade cerrado correctamente\n\n"
                f"👤 Usuario: {user}\n"
                f"🪙 Symbol: {symbol}\n"
                f"💰 PNL: {result['pnl']:+.2f} USDT\n"
                f"📊 Return: {result['pnl_percent']:+.2f}%\n"
                f"⏳ Tiempo: {result['days_in_trade']} días"
            )
        print(message_text)
        send_message(chat_id, message_text)
        
    except Exception as e:
        message_text = f"❌ Error SELL:\n{e}"
        print(message_text)
        send_message(chat_id, message_text)