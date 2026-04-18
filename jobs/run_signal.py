import os
from dotenv import load_dotenv
from datetime import datetime

from alerts.telegram.notifier import TelegramNotifier
from alerts.manager import build_signal_message

from analytics.chart.chart_builder import build_chart
from analytics.pipeline import run_pipeline

from src.config.settings import SYMBOLS
from src.config.paths import BASE_DIR


# ---------------------------
# ⚙️ CONFIG
# ---------------------------
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

notifier = TelegramNotifier(TOKEN, CHAT_ID)

CHARTS_DIR = os.path.join(BASE_DIR, "analytics", "chart", "output")
os.makedirs(CHARTS_DIR, exist_ok=True)


# ---------------------------
# 🚀 FUNCIÓN PRINCIPAL
# ---------------------------
def run():

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    separator_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━
⏰ *Actualización:* {now}
━━━━━━━━━━━━━━━━━━━━━━━
"""
    notifier.send_message(separator_message)

    # ---------------------------
    # ⏱ TIMEFRAMES
    # ---------------------------
    timeframes = [
        ("Semana", "1 Semana", 0.01),
        ("Mes", "1 Mes", 0.02),
    ]

    for SYMBOL in SYMBOLS:

        try:
            print(f"🚀 Procesando {SYMBOL}")

            for label, range_option, prominence in timeframes:

                data = run_pipeline(
                    symbol=SYMBOL,
                    interval="1H",
                    range_option=range_option,
                    prominence=prominence,
                    window_swings=10
                )

                # ---------------------------
                # 📊 EXTRAER DATOS
                # ---------------------------
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

                # ---------------------------
                # 🎯 CONDICIONES
                # ---------------------------
                buy_signal = signal in ["BUY", "STRONG BUY"]
                sell_signal = signal in ["SELL", "STRONG SELL"]

                # ---------------------------
                # 🧾 MENSAJE
                # ---------------------------
                message = build_signal_message(
                    f"{SYMBOL} ({label})",
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

                # ---------------------------
                # 📊 GRÁFICA
                # ---------------------------
                fig = build_chart(df, avg_peak, avg_valley, trend)

                image_path = os.path.join(
                    CHARTS_DIR,
                    f"{SYMBOL}_{label}.png"
                )

                fig.write_image(image_path)

                # ---------------------------
                # 📤 ENVÍO
                # ---------------------------
                if buy_signal or sell_signal:

                    if buy_signal:
                        action_text = "🟢 ===== COMPRAR ===== 🟢"
                    else:
                        action_text = "🔴 ===== VENDER ===== 🔴"

                    final_message = (
                        f"{message}\n"
                        f"{action_text}\n"
                        f"📊 Señal: {signal} (Score: {score})\n"
                        f"📚 OrderBook Imbalance: {imbalance:.2f}"
                    )

                    notifier.send_photo(image_path, caption=final_message)

                    print(f"📢 Señal enviada: {SYMBOL} ({label})")

                else:
                    print(f"⏭️ {SYMBOL} ({label}) sin señal")

                # ---------------------------
                # 🧹 LIMPIAR IMAGEN
                # ---------------------------
                if os.path.exists(image_path):
                    os.remove(image_path)

        except Exception as e:
            print(f"❌ Error en {SYMBOL}: {e}")