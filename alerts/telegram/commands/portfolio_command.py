from src.api.telegram.client import send_message
from src.api.binance.client import get_crypto_price

from data.portfolio.storage import load_active_positions



def handle_portfolio_command(chat_id, text):
    try:
        parts = text.split()
        user = parts[1].upper()
        positions = load_active_positions()

        # VALIDAR USUARIO
        if user not in positions:
            message_text = f"❌ No hay posiciones activas para {user}"
            print(message_text)
            send_message(chat_id, message_text)
        else:
            user_positions = positions[user]
            lines = [f"📂 PORTFOLIO {user}\n"]

            total_usdt = 0
            grand_total_pnl = 0
            # RECORRER MONEDAS
            for symbol, trades in user_positions.items():
                symbol_usdt = 0
                symbol_coins = 0
                latest_entry = 0
                current_price = get_crypto_price(symbol)                # SUMAR POSICIONES

                total_pnl = 0
                total_pnl_percent = 0
                for trade in trades:
                    invested = trade["usdt_invested"]
                    coins = trade["coin_amount"]
                    entry_price = trade["entry_price"]
                    current_value = coins * current_price
                    pnl = current_value - invested
                    pnl_percent = (pnl / invested) * 100
                    symbol_usdt += invested
                    symbol_coins += coins
                    total_pnl += pnl
                    total_pnl_percent += pnl_percent
                    latest_entry = entry_price

                total_usdt += symbol_usdt
                grand_total_pnl += total_pnl
                coin_name = symbol.replace("USDT", "")

                line = (
                    f"\n{symbol}\n"
                    f"• {symbol_usdt:.2f} USDT          <--- Dinero ingresado \n"
                    f"• Entry: {latest_entry:.4f}\n"
                    f"• Current: {current_price:.4f}\n"
                    f"• {symbol_coins:.6f} {coin_name}\n"
                    f"• PNL: {total_pnl:+.2f} USDT ({total_pnl_percent:+.2f}%)"
                )
                lines.append(line)
            lines.append(f"\n🔥 Ganancias: {grand_total_pnl:+.2f} USDT")
            lines.append(f"💵 Total invertido: {total_usdt:.2f} USDT")
            final_message = "\n".join(lines)
            print(final_message)
            send_message(chat_id, final_message)
    except Exception as e:
        message_text = f"❌ Error PORTFOLIO:\n{e}"
        print(message_text)
        send_message(chat_id, message_text)