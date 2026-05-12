import os

from analytics.pipeline import run_pipeline
from alerts.manager import build_signal_message
from analytics.chart.chart_builder import build_chart

from src.config.paths import BASE_DIR

CHARTS_DIR = os.path.join(
    BASE_DIR,
    "analytics",
    "chart",
    "output"
)

os.makedirs(CHARTS_DIR, exist_ok=True)


def generate_signal_data(symbol, label, range_option, prominence):

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
    # CONDICIONES ESTRICTAS
    # =========================
    buy_signal = (
        avg_valley is not None and
        price < avg_valley and
        trend == "Bearish" and
        signal in ["BUY", "STRONG BUY"] and
        vwap > price
    )

    sell_signal = (
        avg_peak is not None and
        price > avg_peak and
        trend == "Bullish" and
        signal in ["SELL", "STRONG SELL"] and
        vwap < price
    )

    # =========================
    # ACTION TEXT
    # =========================
    if buy_signal:
        action_text = "🟢 ===== COMPRAR ===== 🟢"

    elif sell_signal:
        action_text = "🔴 ===== VENDER ===== 🔴"

    else:
        action_text = "📂 ===== PORTFOLIO TRACKING ===== 📂"

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

    final_message = (
        f"{message}\n"
        f"{action_text}\n"
        f"📊 Señal: {signal} (Score: {score})\n"
        f"📚 OrderBook Imbalance: {imbalance:.2f}"
    )

    # =========================
    # GRÁFICA
    # =========================
    fig = build_chart(
        df=df,
        avg_peak=avg_peak,
        avg_valley=avg_valley,
        trend=trend,
        signal=signal
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

    # =========================
    # CONDICIONES
    # =========================
    buy_signal = (
        avg_valley is not None and
        price < avg_valley and
        trend == "Bearish" and
        signal in ["BUY", "STRONG BUY"] and
        vwap > price
    )

    sell_signal = (
        avg_peak is not None and
        price > avg_peak and
        trend == "Bullish" and
        signal in ["SELL", "STRONG SELL"] and
        vwap < price
    )

    return {
        "message": final_message,
        "image_path": image_path,
        "buy_signal": buy_signal,
        "sell_signal": sell_signal
    }