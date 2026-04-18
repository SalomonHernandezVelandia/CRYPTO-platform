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

PROMINENCE = 0.01   # sensibilidad fija
WINDOW_SWINGS = 10  # ventana fija

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

            # ---------------------------
            # FILTRO SEMANA
            # ---------------------------
            df_week = df.loc[df.index >= df.index.max() - pd.Timedelta(days=7)]
            if "fundingRate" in df_week.columns:
                current_funding = df_week["fundingRate"].iloc[-1]
            else:
                current_funding = 0

            # ---------------------------
            # 📈 TREND (igual dashboard)
            # ---------------------------
            df_week["ma_20"] = df_week["close"].rolling(20).mean()
            df_week["ma_50"] = df_week["close"].rolling(50).mean()
            df_week["cum_vol"] = df_week["volume"].cumsum()
            df_week["cum_vol_price"] = (df_week["close"] * df_week["volume"]).cumsum()
            df_week["vwap"] = df_week["cum_vol_price"] / df_week["cum_vol"]

            current_trend = "Bullish" if df_week["ma_20"].iloc[-1] > df_week["ma_50"].iloc[-1] else "Bearish"


            # ---------------------------
            # 🌍 CONTEXTO DE MERCADO
            # ---------------------------
            df_week["volatility"] = df_week["close"].rolling(20).std()
            df_week["range"] = df_week["high"].rolling(20).max() - df_week["low"].rolling(20).min()

            current_volatility = df_week["volatility"].iloc[-1]
            current_range = df_week["range"].iloc[-1]

            if current_volatility > df_week["volatility"].mean() * 1.5:
                market_context = "volatile"

            elif current_range < df_week["range"].mean() * 0.8:
                market_context = "ranging"

            else:
                market_context = "trending"

            price = df_week["close"].iloc[-1]

            # ---------------------------
            # VWAP SEMANAL
            # ---------------------------
            vwap_week = (df_week["close"] * df_week["volume"]).sum() / df_week["volume"].sum()

            # ---------------------------
            # SWINGS
            # ---------------------------
            swings = get_trade_swings(df_week, prominence=PROMINENCE)

            peak_y, valley_y = [], []

            for idx, typ in swings:
                if typ == "peak":
                    peak_y.append(df_week["close"].iloc[idx])
                else:
                    valley_y.append(df_week["close"].iloc[idx])

            # ---------------------------
            # PROMEDIOS DINÁMICOS
            # ---------------------------
            recent_peaks = peak_y[-WINDOW_SWINGS:] if len(peak_y) > 0 else []
            recent_valleys = valley_y[-WINDOW_SWINGS:] if len(valley_y) > 0 else []

            peak_weights = np.linspace(1.5, 1.0, len(recent_peaks)) if recent_peaks else []
            valley_weights = np.linspace(1.5, 1.0, len(recent_valleys)) if recent_valleys else []

            avg_peak = weighted_average(recent_peaks, peak_weights) if len(recent_peaks) > 0 else None
            avg_valley = weighted_average(recent_valleys, valley_weights) if len(recent_valleys) > 0 else None

            # ---------------------------
            # TRADES REALES
            # ---------------------------
            trades_week = len(swings)

            # ---------------------------
            # MENSAJE
            # ---------------------------
            message = build_signal_message(
                SYMBOL,
                {
                    "price": price,
                    "vwap_week": vwap_week,
                    "trades_week": trades_week,
                    "w_peak": avg_peak,
                    "w_valley": avg_valley,
                    "trend": current_trend,
                    "context": market_context,
                    "funding": current_funding   
                }
            )

            # ---------------------------
            # 📊 CREAR GRÁFICA
            # ---------------------------
            fig = build_chart(df_week, avg_peak, avg_valley, current_trend)

            # 🔥 guardar imagen
            image_path = os.path.join(CHARTS_DIR, f"{SYMBOL}.png")
            fig.write_image(image_path)

            # ---------------------------
            # 📤 ENVIAR A TELEGRAM
            # ---------------------------
            notifier.send_photo(image_path, caption=message)

            print("📸 Señal + gráfica enviada")

        except Exception as e:
            print("❌ Error:", e)