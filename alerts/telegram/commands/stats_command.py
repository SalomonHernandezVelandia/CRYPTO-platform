from src.api.telegram.client import send_message
from src.api.binance.client import get_crypto_price

from data.portfolio.storage import load_trade_history, load_active_positions



def handle_stats_command(chat_id, text):
    try:
        parts = text.split()
        user = parts[1].upper()
        positions = load_active_positions()
        history = load_trade_history()

        # CAPITAL ACTIVO
        active_capital = 0
        floating_pnl = 0
        if user in positions:
            for symbol, trades in positions[user].items():
                current_price = get_crypto_price(symbol)
                for trade in trades:
                    invested = trade["usdt_invested"]
                    coins = trade["coin_amount"]
                    current_value = coins * current_price
                    pnl = current_value - invested
                    active_capital += invested
                    floating_pnl += pnl

        # HISTORIAL USUARIO
        user_history = [
            trade
            for trade in history
            if trade["user"] == user
        ]
        total_realized = 0
        wins = 0
        losses = 0
        best_trade = None
        worst_trade = None
        total_days = 0

        for trade in user_history:
            pnl = trade["pnl"]
            total_realized += pnl
            total_days += trade["days_in_trade"]

            # WIN / LOSS
            if pnl > 0:
                wins += 1
            else:
                losses += 1

            # BEST TRADE
            if best_trade is None or pnl > best_trade:
                best_trade = pnl

            # WORST TRADE
            if worst_trade is None or pnl < worst_trade:
                worst_trade = pnl
        total_trades = len(user_history)

        # WIN RATE
        if total_trades > 0:
            win_rate = (wins / total_trades) * 100
            loss_rate = (losses / total_trades) * 100
            avg_days = total_days / total_trades
        else:
            win_rate = 0
            loss_rate = 0
            avg_days = 0

        # MENSAJE
        message_text = (
            f"📊 STATS {user}\n\n"

            f"💵 Capital activo: {active_capital:.2f} USDT\n"
            f"🔥 PNL flotante: {floating_pnl:+.2f} USDT\n\n"

            f"🏆 Ganancia realizada: {total_realized:+.2f} USDT\n"
            f"📈 Trades cerrados: {total_trades}\n"
            f"✅ Win Rate: {win_rate:.2f}%\n"
            f"❌ Loss Rate: {loss_rate:.2f}%\n\n"

            f"🥇 Mejor trade: {best_trade if best_trade is not None else 0:+.2f} USDT\n"
            f"💀 Peor trade: {worst_trade if worst_trade is not None else 0:+.2f} USDT\n\n"

            f"⏳ Tiempo promedio trade: {avg_days:.1f} días"
        )
        print(message_text)
        send_message(chat_id, message_text)
    except Exception as e:
        message_text = f"❌ Error STATS:\n{e}"
        print(message_text)
        send_message(chat_id, message_text)