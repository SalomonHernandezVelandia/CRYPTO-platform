from analytics.pipeline import run_pipeline
from analytics.signals.rapid_reversal import detect_rapid_reversal

from src.config.settings import SYMBOLS
from src.api.telegram.client import send_message


TIMEFRAMES = ["15m", "1h"]


# ==========================================
# FAST ALERTS
# ==========================================
def run_fast_alerts():
    print("⚡ Ejecutando fast alerts...")
    alerts_found = 0

    for symbol in SYMBOLS:
        # RECORRER TEMPORALIDADES
        for timeframe in TIMEFRAMES:
            try:
                data = run_pipeline(
                    symbol=symbol,
                    interval=timeframe,
                    range_option="1 Semana",
                    prominence=0.01,
                    window_swings=10
                )
                df = data["df"]
                trend = data["trend"]

                # DETECTAR PATRONES
                rapid_signal = detect_rapid_reversal(df, trend)
                if rapid_signal is None:
                    continue

                alerts_found += 1

                # MENSAJE
                title = rapid_signal.get(
                    "message",
                    "⚠️ POSIBLE CAMBIO DE TENDENCIA"
                )

                message = (
                    f"{title}\n\n"
                    f"🪙 {symbol}\n"
                    f"⏰ Temporalidad: {timeframe}\n"
                    f"📈 Movimiento: "
                    f"{rapid_signal['movement']:.2f}%\n"
                    f"🔥 Explosividad: "
                    f"{rapid_signal['explosive']}\n"
                    f"🧠 Patrón: "
                    f"{rapid_signal['pattern']}"
                )
                send_message(text=message)
                print(
                    f"✅ Fast alert enviada: "
                    f"{symbol} {timeframe}"
                )

            except Exception as e:
                print(
                    f"❌ Fast alert error "
                    f"{symbol} {timeframe}: {e}"
                )


    # ======================================
    # NO HUBO ALERTAS
    # ======================================
    if alerts_found == 0:
        print("⚠️ Sin alertas rápidas en esta ronda")