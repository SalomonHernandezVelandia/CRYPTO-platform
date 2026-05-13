import os

from analytics.pipeline import run_pipeline
from analytics.chart.chart_builder import build_chart

from alerts.manager import build_signal_message

from src.config.paths import BASE_DIR

from data.portfolio.storage import load_active_positions


CHARTS_DIR = os.path.join(
    BASE_DIR,
    "analytics",
    "chart",
    "output"
)

os.makedirs(CHARTS_DIR, exist_ok=True)


def generate_signal_data(
    symbol,
    label="Semana",
    range_option="1 Semana",
    prominence=0.01
):

    # =========================
    # PIPELINE
    # =========================
    data = run_pipeline(
        symbol=symbol,
        interval="1H",
        range_option=range_option,
        prominence=prominence,
        window_swings=10
    )

    # =========================
    # EXTRAER DATOS
    # =========================
    df = data["df"]

    trend = data["trend"]

    context = data["context"]

    avg_peak, avg_valley = data["levels"]

    signal_data = data["signal"]

    funding = data["funding"]

    peak_x, peak_y, valley_x, valley_y = data["swings"]

    trades = len(peak_y) + len(valley_y)

    imbalance = data["orderbook"]["imbalance"]

    price = df["close"].iloc[-1]

    vwap = df["vwap"].iloc[-1]

    signal = signal_data["signal"]

    score = signal_data["score"]

    # =========================
    # MENSAJE
    # =========================
    message = build_signal_message(
        f"{symbol} ({label})",
        {
            "price": price,
            "vwap_week": vwap,
            "trades_week": trades,
            "w_peak": avg_peak,
            "w_valley": avg_valley,
            "trend": trend,
            "context": context,
            "funding": funding
        }
    )

    # =========================
    # TRADES ACTIVOS
    # =========================
    positions = load_active_positions()

    symbol_trades = []

    for username, user_positions in positions.items():

        if symbol not in user_positions:
            continue

        if username.upper() == "SALOMON":
            trade_color = "#FFD700"
        else:
            trade_color = "#C77DFF"

        for trade in user_positions[symbol]:

            symbol_trades.append({
                "date": trade["entry_date"],
                "price": trade["entry_price"],
                "user": username,
                "color": trade_color
            })

    # =========================
    # GRÁFICA
    # =========================
    fig = build_chart(
        df=df,
        avg_peak=avg_peak,
        avg_valley=avg_valley,
        trend=trend,
        signal=signal,
        trades=symbol_trades
    )

    image_path = os.path.join(
        CHARTS_DIR,
        f"{symbol}_{label}.png"
    )

    fig.write_image(
        image_path,
        width=1600,
        height=900,
        scale=2
    )

    final_message = (
        f"{message}\n"
        f"📊 Señal: {signal} (Score: {score})\n"
        f"📚 OrderBook Imbalance: {imbalance:.2f}"
    )

    return {
        "message": final_message,
        "image_path": image_path,
        "signal": signal
    }