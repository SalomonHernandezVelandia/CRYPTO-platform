import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from scipy.signal import find_peaks

from alerts.telegram.notifier import TelegramNotifier
from alerts.manager import build_signal_message

from app.dashboard import load_data
from analytics.chart.chart_builder import build_chart

from app.dashboard import load_funding

from datetime import datetime

# ---------------------------
# ⚙️ CONFIG
# ---------------------------
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT",
    "DOGEUSDT", "ADAUSDT", "LINKUSDT", "XMRUSDT",
    "AVAXUSDT", "HBARUSDT", "SHIBUSDT", "PEPEUSDT", "XLMUSDT"
]

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

notifier = TelegramNotifier(TOKEN, CHAT_ID)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(BASE_DIR, "analytics", "chart", "output")

os.makedirs(CHARTS_DIR, exist_ok=True)


# ---------------------------
# 🔍 SWINGS (igual dashboard)
# ---------------------------
def get_trade_swings(df, prominence=0.05):

    prices = df["close"].values

    peaks, _ = find_peaks(prices, prominence=prominence * np.mean(prices))
    valleys, _ = find_peaks(-prices, prominence=prominence * np.mean(prices))

    events = [(p, "peak") for p in peaks] + [(v, "valley") for v in valleys]
    events = sorted(events, key=lambda x: x[0])

    filtered = []
    last_type = None

    for idx, typ in events:

        if typ != last_type:
            filtered.append((idx, typ))
            last_type = typ
        else:
            prev_idx, _ = filtered[-1]

            if typ == "peak":
                if prices[idx] > prices[prev_idx]:
                    filtered[-1] = (idx, typ)

            elif typ == "valley":
                if prices[idx] < prices[prev_idx]:
                    filtered[-1] = (idx, typ)

    return filtered


def weighted_average(values, weights):
    if len(values) == 0:
        return None
    return np.sum(np.array(values) * np.array(weights)) / np.sum(weights)


def process_timeframe(df, days, symbol, prominence, window):
    df_tf = df.loc[df.index >= df.index.max() - pd.Timedelta(days=days)].copy()

    if df_tf.empty:
        return None

    # ---------------------------
    # 📈 INDICADORES
    # ---------------------------
    df_tf["ma_20"] = df_tf["close"].rolling(20).mean()
    df_tf["ma_50"] = df_tf["close"].rolling(50).mean()
    df_tf["cum_vol"] = df_tf["volume"].cumsum()
    df_tf["cum_vol_price"] = (df_tf["close"] * df_tf["volume"]).cumsum()
    df_tf["vwap"] = df_tf["cum_vol_price"] / df_tf["cum_vol"]

    trend = "Bullish" if df_tf["ma_20"].iloc[-1] > df_tf["ma_50"].iloc[-1] else "Bearish"

    # ---------------------------
    # 🌍 CONTEXTO
    # ---------------------------
    df_tf["volatility"] = df_tf["close"].rolling(20).std()
    df_tf["range"] = df_tf["high"].rolling(20).max() - df_tf["low"].rolling(20).min()

    if df_tf["volatility"].iloc[-1] > df_tf["volatility"].mean() * 1.5:
        context = "volatile"
    elif df_tf["range"].iloc[-1] < df_tf["range"].mean() * 0.8:
        context = "ranging"
    else:
        context = "trending"

    # ---------------------------
    # 📊 SWINGS
    # ---------------------------
    swings = get_trade_swings(df_tf, prominence=prominence)
    
    peak_y, valley_y = [], []

    for idx, typ in swings:
        if typ == "peak":
            peak_y.append(df_tf["close"].iloc[idx])
        else:
            valley_y.append(df_tf["close"].iloc[idx])

    recent_peaks = peak_y[-window:] if len(peak_y) >= window else peak_y
    recent_valleys = valley_y[-window:] if len(valley_y) >= window else valley_y

    if context == "ranging":
        valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
        peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))

    elif context == "trending":

        if trend == "Bullish":
            valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
            peak_weights = np.linspace(0.5, 1.0, len(recent_peaks))
        else:
            peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))
            valley_weights = np.linspace(0.5, 1.0, len(recent_valleys))

    elif context == "volatile":
        valley_weights = np.linspace(0.7, 1.0, len(recent_valleys))
        peak_weights = np.linspace(0.7, 1.0, len(recent_peaks))

    avg_peak = weighted_average(recent_peaks, peak_weights)
    avg_valley = weighted_average(recent_valleys, valley_weights)

    # ---------------------------
    # 📊 MÉTRICAS
    # ---------------------------
    price = df_tf["close"].iloc[-1]
    vwap = (df_tf["close"] * df_tf["volume"]).sum() / df_tf["volume"].sum()

    return {
        "df": df_tf,
        "price": price,
        "vwap": vwap,
        "trend": trend,
        "context": context,
        "avg_peak": avg_peak,
        "avg_valley": avg_valley,
        "trades": len(swings)
    }

# ---------------------------
# 🚀 FUNCIÓN PRINCIPAL
# ---------------------------
def run():

    # ---------------------------
    # 🧭 SEPARADOR DE BLOQUE
    # ---------------------------
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    separator_message = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━
    ⏰ *Actualización:* {now}
    ━━━━━━━━━━━━━━━━━━━━━━━
    """

    notifier.send_message(separator_message)

    for SYMBOL in SYMBOLS:

        try:
            print(f"🚀 Procesando {SYMBOL}")

            df = load_data(SYMBOL)
            funding_df = load_funding(SYMBOL)

            if funding_df is not None:
                df = df.merge(funding_df, left_index=True, right_index=True, how="left")
                df["fundingRate"] = df["fundingRate"].ffill()

            # funding seguro
            if "fundingRate" in df.columns and not df["fundingRate"].isna().all():
                current_funding = df["fundingRate"].iloc[-1]
            else:
                current_funding = 0

            # ---------------------------
            # ⏱ TIMEFRAMES
            # ---------------------------
            timeframes = [
                ("Semana", 7, 0.01),
                ("Mes", 30, 0.02)
            ]
            WINDOW = 10

            for label, days, prominence in timeframes:

                result = process_timeframe(
                    df,
                    days,
                    SYMBOL,
                    prominence,
                    WINDOW
                )

                if result is None:
                    continue

                # ---------------------------
                # EXTRAER DATOS
                # ---------------------------
                price = result["price"]
                vwap = result["vwap"]
                avg_peak = result["avg_peak"]
                avg_valley = result["avg_valley"]
                trend = result["trend"]
                context = result["context"]

                # ---------------------------
                # 🎯 CONDICIONES
                # ---------------------------
                buy_signal = (
                    avg_valley is not None and
                    price < avg_valley and
                    price < vwap and
                    trend == "Bearish" and
                    current_funding > 0
                )

                sell_signal = (
                    avg_peak is not None and
                    price > avg_peak and
                    price > vwap and
                    trend == "Bullish" and
                    context == "trending" and
                    current_funding < 0
                )

                # ---------------------------
                # 🧾 MENSAJE
                # ---------------------------
                message = build_signal_message(
                    f"{SYMBOL} ({label})",
                    {
                        "price": price,
                        "vwap_week": vwap,
                        "trades_week": result["trades"],
                        "w_peak": avg_peak,
                        "w_valley": avg_valley,
                        "trend": trend,
                        "context": context,
                        "funding": current_funding
                    }
                )

                # ---------------------------
                # 📊 GRÁFICA
                # ---------------------------
                fig = build_chart(
                    result["df"],
                    avg_peak,
                    avg_valley,
                    trend
                )

                image_path = os.path.join(
                    CHARTS_DIR,
                    f"{SYMBOL}_{label}.png"
                )

                fig.write_image(image_path)

                # ---------------------------
                # 📤 ENVÍO CON FILTRO
                # ---------------------------
                if buy_signal or sell_signal:

                    if buy_signal:
                        action_text = "🟢 ===== COMPRAR!!! ===== 🟢"
                    else:
                        action_text = "🔴 ===== VENDER!!! ===== 🔴"

                    final_message = f"{message}\n{action_text}"

                    notifier.send_photo(image_path, caption=final_message)

                    print(f"📢 Señal enviada: {SYMBOL} {label}")

                else:
                    print(f"⏭️ {SYMBOL} {label} sin señal")

                # limpiar imagen
                if os.path.exists(image_path):
                    os.remove(image_path)

        except Exception as e:
            print(f"❌ Error en {SYMBOL}: {e}")