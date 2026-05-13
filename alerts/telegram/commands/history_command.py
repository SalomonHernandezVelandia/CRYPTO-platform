from src.api.telegram.client import send_message

from data.portfolio.storage import load_trade_history


def handle_history_command(chat_id, text):
    try:
        parts = text.split()
        user = parts[1].upper()
        history = load_trade_history()                  # Carga historial
        user_history = [
            trade for trade in history
            if trade["user"] == user
        ]

        if len(user_history) == 0:
            message_text = (f"❌ No hay histórico para {user}")
            print(message_text)
            send_message(chat_id, message_text)
        else:
            lines = [f"📜 HISTORIAL {user}\n"]
            for trade in user_history:
                line = (
                    f"{trade['symbol']} | "
                    f"PNL: {trade['pnl']:.2f} USDT | "
                    f"{trade['pnl_percent']:.2f}% | "
                    f"{trade['days_in_trade']} días"
                )
                lines.append(line)
            message_text = "\n".join(lines)
        print(message_text)
        send_message(chat_id, message_text)

    except Exception as e:
        message_text = f"❌ Error HISTORY:\n{e}"
        print(message_text)
        send_message(chat_id, message_text)