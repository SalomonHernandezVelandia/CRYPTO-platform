from analytics.pipeline import run_pipeline
from alerts.telegram.notifier import TelegramNotifier

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

notifier = TelegramNotifier(TOKEN, CHAT_ID)

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
]


def run_fast_alerts():

    for symbol in SYMBOLS:

        try:

            data = run_pipeline(
                symbol=symbol,
                interval="15M",
                range_option="1 Semana",
                prominence=0.01,
                window_swings=10
            )

            df = data["df"]

            last_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]

            last_size = abs(last_candle["close"] - last_candle["open"])
            prev_size = abs(prev_candle["close"] - prev_candle["open"])

            # ==================================
            # MOVIMIENTO FUERTE
            # ==================================
            if prev_size > 0 and last_size >= prev_size * 3:

                direction = "🟢 FUERTE SUBIDA" if (
                    last_candle["close"] > last_candle["open"]
                ) else "🔴 FUERTE CAÍDA"

                pct = (
                    abs(last_candle["close"] - last_candle["open"])
                    / last_candle["open"]
                ) * 100

                message = (
                    f"{direction}\n\n"
                    f"🪙 {symbol}\n"
                    f"📊 Movimiento: {pct:.2f}%\n"
                    f"⏰ Vela 15M explosiva"
                )

                notifier.send_message(message)

                print(f"ALERTA {symbol}")

        except Exception as e:
            print(f"Fast alert error {symbol}: {e}")