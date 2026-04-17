def build_signal_message(symbol, signal_data, extra_data):

    signal = signal_data["signal"]
    score = signal_data["score"]

    price = extra_data["price"]
    vwap = extra_data["vwap"]
    trend = extra_data["trend"]
    funding = extra_data["funding"]
    imbalance = extra_data["imbalance"]

    # 🎯 Emoji dinámico
    if "BUY" in signal:
        emoji = "🟢"
    elif "SELL" in signal:
        emoji = "🔴"
    else:
        emoji = "🟡"

    message = f"""
{emoji} *{symbol}*

📊 *Señal:* {signal}
🧠 *Score:* {score}

💰 *Precio:* {price:.2f}
📉 *VWAP:* {vwap:.2f}

📈 *Trend:* {trend}
💸 *Funding:* {funding:.5f}
📚 *Imbalance:* {imbalance:.2f}
"""

    return message