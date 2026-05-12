import time
import requests
import os
import pandas as pd

from dotenv import load_dotenv

from data.portfolio.manager import add_position, sell_position, get_trade_history

from data.portfolio.storage import load_trade_history, load_active_positions


load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

SEND_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_telegram_message(chat_id, text):

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    requests.post(SEND_URL, json=payload)


offset = None


def get_crypto_price(symbol):

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    response = requests.get(url).json()

    return float(response["price"])


def get_historical_price(symbol, date_string):

    # Binance Klines API
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 1
    }

    # Convertir fecha a timestamp
    dt = pd.to_datetime(date_string)

    timestamp = int(dt.timestamp() * 1000)

    params["startTime"] = timestamp

    response = requests.get(url, params=params).json()

    # Close price
    close_price = float(response[0][4])

    return close_price


def check_telegram_updates():
    global offset

    params = {}

    if offset:
        params["offset"] = offset

    response = requests.get(URL, params=params).json()

    print(response)

    for result in response["result"]:

        offset = result["update_id"] + 1

        message = (
            result.get("message")
            or result.get("channel_post")
            or {}
        )

        chat_id = message.get("chat", {}).get("id")

        text = message.get("text", "")

        user_data = message.get("from", {})
        user = (
            user_data.get("username")
            or user_data.get("first_name")
            or str(user_data.get("id"))
        )
        print(message)

        # =========================
        # ADD COMMAND
        # =========================
        if text.startswith("/add"):

            try:

                parts = text.split()

                user = parts[1].upper()
                symbol = parts[2].upper()
                usdt = float(parts[3])

                # =========================
                # FECHA OPCIONAL
                # =========================
                if len(parts) >= 5:

                    entry_date = pd.to_datetime(
                        " ".join(parts[4:])
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    price = get_historical_price(
                        symbol,
                        entry_date
                    )

                else:

                    entry_date = None

                    price = get_crypto_price(symbol)

                amount = add_position(
                    user=user,
                    symbol=symbol,
                    usdt_invested=usdt,
                    entry_price=price,
                    entry_date=entry_date
                )

                message_text = (
                    f"✅ Trade agregado correctamente\n\n"
                    f"👤 Usuario: {user}\n"
                    f"🪙 Symbol: {symbol}\n"
                    f"💵 Inversión: {usdt:.2f} USDT\n"
                    f"📈 Entry: {price:.4f}\n"
                    f"🧮 Coins: {amount:.6f}"
                )

                print(message_text)

                send_telegram_message(chat_id, message_text)

            except Exception as e:

                message_text = f"❌ Error ADD:\n{e}"

                print(message_text)

                send_telegram_message(chat_id, message_text)


        # =========================
        # SELL COMMAND
        # =========================
        if text.startswith("/sell"):

            try:

                parts = text.split()

                user = parts[1].upper()
                symbol = parts[2].upper()

                price = get_crypto_price(symbol)

                result = sell_position(
                    user=user,
                    symbol=symbol,
                    exit_price=price
                )

                if result is None:

                    message_text = "❌ No existe posición activa"

                    print(message_text)

                    send_telegram_message(chat_id, message_text)

                else:

                    message_text = (
                        f"✅ Trade cerrado correctamente\n\n"
                        f"👤 Usuario: {user}\n"
                        f"🪙 Symbol: {symbol}\n"
                        f"💰 PNL: {result['pnl']:+.2f} USDT\n"
                        f"📊 Return: {result['pnl_percent']:+.2f}%\n"
                        f"⏳ Tiempo: {result['days_in_trade']} días"
                    )

                    print(message_text)

                    send_telegram_message(chat_id, message_text)

            except Exception as e:

                message_text = f"❌ Error SELL:\n{e}"

                print(message_text)

                send_telegram_message(chat_id, message_text)

        
        # =========================
        # HISTORY COMMAND
        # =========================
        if text.startswith("/history"):

            try:

                parts = text.split()

                user = parts[1].upper()

                history = load_trade_history()

                user_history = [
                    trade for trade in history
                    if trade["user"] == user
                ]

                if len(user_history) == 0:

                    message_text = f"❌ No hay histórico para {user}"

                    print(message_text)

                    send_telegram_message(chat_id, message_text)

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

                    final_message = "\n".join(lines)

                    print(final_message)

                    send_telegram_message(chat_id, final_message)

            except Exception as e:

                message_text = f"❌ Error HISTORY:\n{e}"

                print(message_text)

                send_telegram_message(chat_id, message_text)


        # =========================
        # PORTFOLIO COMMAND
        # =========================
        if text.startswith("/portfolio"):

            try:

                parts = text.split()

                user = parts[1].upper()

                positions = load_active_positions()

                # =========================
                # VALIDAR USUARIO
                # =========================
                if user not in positions:

                    message_text = f"❌ No hay posiciones activas para {user}"

                    print(message_text)

                    send_telegram_message(chat_id, message_text)

                else:

                    user_positions = positions[user]

                    lines = [f"📂 PORTFOLIO {user}\n"]

                    total_usdt = 0
                    grand_total_pnl = 0

                    # =========================
                    # RECORRER MONEDAS
                    # =========================
                    for symbol, trades in user_positions.items():

                        symbol_usdt = 0
                        symbol_coins = 0

                        latest_entry = 0

                        # =========================
                        # SUMAR POSICIONES
                        # =========================
                        current_price = get_crypto_price(symbol)

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

                    lines.append(
                        f"\n🔥 Ganancias: {grand_total_pnl:+.2f} USDT"
                    )

                    lines.append(
                        f"💵 Total invertido: {total_usdt:.2f} USDT"
                    )

                    final_message = "\n".join(lines)

                    print(final_message)

                    send_telegram_message(chat_id, final_message)

            except Exception as e:

                message_text = f"❌ Error PORTFOLIO:\n{e}"

                print(message_text)

                send_telegram_message(chat_id, message_text)

        # =========================
        # ANALYZE COMMAND
        # =========================
        if text.startswith("/analyze"):

            try:

                parts = text.split()

                symbol = parts[1].upper()

                send_telegram_message(
                    chat_id,
                    f"📊 Analizando {symbol}..."
                )

                from alerts.services.signal_service import generate_signal_data

                # =========================
                # SEMANA
                # =========================
                week_result = generate_signal_data(
                    symbol=symbol,
                    label="Semana",
                    range_option="1 Semana",
                    prominence=0.01
                )

                send_telegram_message(
                    chat_id,
                    week_result["message"]
                )

                # opcional imagen
                with open(week_result["image_path"], "rb") as photo:

                    requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                        data={"chat_id": chat_id},
                        files={"photo": photo}
                    )

                # =========================
                # MES
                # =========================
                month_result = generate_signal_data(
                    symbol=symbol,
                    label="Mes",
                    range_option="1 Mes",
                    prominence=0.02
                )

                send_telegram_message(
                    chat_id,
                    month_result["message"]
                )

                with open(month_result["image_path"], "rb") as photo:

                    requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                        data={"chat_id": chat_id},
                        files={"photo": photo}
                    )

                # =========================
                # LIMPIAR
                # =========================
                os.remove(week_result["image_path"])
                os.remove(month_result["image_path"])

            except Exception as e:

                message_text = f"❌ Error ANALYZE:\n{e}"

                print(message_text)

                send_telegram_message(chat_id, message_text)

        # =========================
        # STATS COMMAND
        # =========================
        if text.startswith("/stats"):

            try:

                parts = text.split()

                user = parts[1].upper()

                positions = load_active_positions()

                history = load_trade_history()

                # =========================
                # CAPITAL ACTIVO
                # =========================
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

                # =========================
                # HISTORIAL USUARIO
                # =========================
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

                    # =========================
                    # WIN / LOSS
                    # =========================
                    if pnl > 0:
                        wins += 1
                    else:
                        losses += 1

                    # =========================
                    # BEST TRADE
                    # =========================
                    if best_trade is None or pnl > best_trade:
                        best_trade = pnl

                    # =========================
                    # WORST TRADE
                    # =========================
                    if worst_trade is None or pnl < worst_trade:
                        worst_trade = pnl

                total_trades = len(user_history)

                # =========================
                # WIN RATE
                # =========================
                if total_trades > 0:

                    win_rate = (wins / total_trades) * 100

                    loss_rate = (losses / total_trades) * 100

                    avg_days = total_days / total_trades

                else:

                    win_rate = 0
                    loss_rate = 0
                    avg_days = 0

                # =========================
                # MENSAJE
                # =========================
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

                send_telegram_message(chat_id, message_text)

            except Exception as e:

                message_text = f"❌ Error STATS:\n{e}"

                print(message_text)

                send_telegram_message(chat_id, message_text)
