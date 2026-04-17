import time
from analytics.signals.signal_engine import compute_signal
from alerts.telegram.notifier import TelegramNotifier
from alerts.manager import build_signal_message

from exchange_API.binance.client import get_order_book
from app.dashboard import load_data, load_funding  # reutilizas

import os
from dotenv import load_dotenv

SYMBOL = "BTCUSDT"

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

notifier = TelegramNotifier(TOKEN, CHAT_ID)

last_signal = None

while True:

    try:
        df = load_data(SYMBOL)
        funding_df = load_funding(SYMBOL)

        if funding_df is not None:
            df = df.merge(funding_df, left_index=True, right_index=True, how="left")
            df["fundingRate"] = df["fundingRate"].ffill()

        # ---------------------------
        # 📊 Datos actuales
        # ---------------------------
        price = df["close"].iloc[-1]
        vwap = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
        vwap = vwap.iloc[-1]

        df["ma_20"] = df["close"].rolling(20).mean()
        df["ma_50"] = df["close"].rolling(50).mean()
        trend = "bullish" if df["ma_20"].iloc[-1] > df["ma_50"].iloc[-1] else "bearish"

        funding = df["fundingRate"].iloc[-1] if "fundingRate" in df else 0

        orderbook = get_order_book(SYMBOL, limit=100)
        bids = [(float(p), float(q)) for p, q in orderbook["bids"]]
        asks = [(float(p), float(q)) for p, q in orderbook["asks"]]

        bid_vol = sum(q for _, q in bids)
        ask_vol = sum(q for _, q in asks)
        imbalance = bid_vol / (bid_vol + ask_vol)

        # ---------------------------
        # 📍 Simples niveles (puedes mejorar luego)
        # ---------------------------
        avg_valley = df["low"].rolling(20).min().iloc[-1]
        avg_peak = df["high"].rolling(20).max().iloc[-1]

        # ---------------------------
        # 🧠 Señal
        # ---------------------------
        signal_data = compute_signal(
            price, vwap, trend, funding, imbalance, avg_valley, avg_peak
        )

        # ---------------------------
        # 🚨 Enviar si cambia
        # ---------------------------
        if signal_data["signal"] != last_signal and abs(signal_data["score"]) >= 2:
            message = build_signal_message(
                SYMBOL,
                signal_data,
                {
                    "price": price,
                    "vwap": vwap,
                    "trend": trend,
                    "funding": funding,
                    "imbalance": imbalance
                }
            )

            notifier.send_message(message)

            print("Enviado:", signal_data["signal"])

            last_signal = signal_data["signal"]

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)