from datetime import datetime
import pandas as pd

from data.portfolio.storage import (
    load_active_positions,
    save_active_positions,
    load_trade_history,
    save_trade_history
)


def add_position(
    user,
    symbol,
    usdt_invested,
    entry_price,
    entry_date=None
):

    if entry_date is None:
        entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    coin_amount = usdt_invested / entry_price

    positions = load_active_positions()

    # =========================
    # CREAR USUARIO
    # =========================
    if user not in positions:
        positions[user] = {}

    # =========================
    # CREAR SYMBOL
    # =========================
    if symbol not in positions[user]:
        positions[user][symbol] = []

    # =========================
    # AGREGAR TRADE
    # =========================
    positions[user][symbol].append({
        "entry_date": entry_date,
        "entry_price": entry_price,
        "usdt_invested": usdt_invested,
        "coin_amount": coin_amount
    })

    save_active_positions(positions)

    return coin_amount



def sell_position(
    user,
    symbol,
    exit_price,
    exit_date=None
):

    if exit_date is None:
        exit_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    positions = load_active_positions()

    # =========================
    # VALIDACIONES
    # =========================
    if user not in positions:
        return None

    if symbol not in positions[user]:
        return None

    if len(positions[user][symbol]) == 0:
        return None

    # =========================
    # TOMAR POSICIÓN
    # =========================
    trade = positions[user][symbol].pop(0)

    entry_price = trade["entry_price"]
    entry_date = trade["entry_date"]
    usdt_invested = trade["usdt_invested"]
    coin_amount = trade["coin_amount"]

    # =========================
    # CALCULAR RESULTADOS
    # =========================
    final_value = coin_amount * exit_price

    pnl = final_value - usdt_invested

    pnl_percent = (pnl / usdt_invested) * 100

    # =========================
    # CALCULAR DÍAS
    # =========================
    entry_dt = pd.to_datetime(entry_date)
    exit_dt = pd.to_datetime(exit_date)

    days_in_trade = (exit_dt - entry_dt).days

    # =========================
    # GUARDAR HISTÓRICO
    # =========================
    history = load_trade_history()

    history.append({
        "user": user,
        "symbol": symbol,
        "entry_date": entry_date,
        "exit_date": exit_date,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "usdt_invested": usdt_invested,
        "final_value": final_value,
        "pnl": pnl,
        "pnl_percent": pnl_percent,
        "days_in_trade": days_in_trade
    })

    save_trade_history(history)

    # =========================
    # LIMPIAR POSICIÓN
    # =========================
    if len(positions[user][symbol]) == 0:
        del positions[user][symbol]

    if len(positions[user]) == 0:
        del positions[user]

    save_active_positions(positions)

    return {
        "pnl": pnl,
        "pnl_percent": pnl_percent,
        "days_in_trade": days_in_trade
    }



def get_trade_history(user=None):

    history = load_trade_history()

    # =========================
    # FILTRAR USUARIO
    # =========================
    if user is not None:

        history = [
            trade
            for trade in history
            if trade["user"] == user
        ]

    return history