import json
import os

ROOT_PATH = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

ACTIVE_FILE = os.path.join(
    ROOT_PATH,
    "data",
    "portfolio",
    "active_positions.json"
)

HISTORY_FILE = os.path.join(
    ROOT_PATH,
    "data",
    "portfolio",
    "trade_history.json"
)


# =========================
# ACTIVE POSITIONS
# =========================
def load_active_positions():

    if not os.path.exists(ACTIVE_FILE):
        return {}

    with open(ACTIVE_FILE, "r") as f:
        return json.load(f)


def save_active_positions(data):

    with open(ACTIVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# TRADE HISTORY
# =========================
def load_trade_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_trade_history(data):

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# DASHBOARD TRADES
# =========================
def get_all_trades_for_symbol(symbol):

    positions = load_active_positions()

    trades = []

    for user, user_positions in positions.items():

        if symbol not in user_positions:
            continue

        for trade in user_positions[symbol]:

            trades.append({
                "user": user,
                "date": trade["entry_date"],
                "price": trade["entry_price"]
            })

    return trades