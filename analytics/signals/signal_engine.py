def compute_signal(
    price,
    vwap,
    trend,
    funding,
    imbalance,
    avg_valley,
    avg_peak
):
    score = 0

    # ---------------------------
    # 📉 Precio vs VWAP
    # ---------------------------
    if price < vwap:
        score += 1
    else:
        score -= 1

    # ---------------------------
    # 📊 Trend
    # ---------------------------
    if trend == "bullish":
        score += 1
    else:
        score -= 1

    # ---------------------------
    # 💰 Funding
    # ---------------------------
    if funding < 0:
        score += 1
    elif funding > 0:
        score -= 1

    # ---------------------------
    # 📚 Order Book
    # ---------------------------
    if imbalance > 0.55:
        score += 1
    elif imbalance < 0.45:
        score -= 1

    # ---------------------------
    # 📍 Posición en rango
    # ---------------------------
    if avg_valley is not None and price <= avg_valley:
        score += 2
    elif avg_peak is not None and price >= avg_peak:
        score -= 2

    # ---------------------------
    # 🎯 Interpretación
    # ---------------------------
    if score >= 3:
        signal = "STRONG BUY"
    elif score >= 1:
        signal = "BUY"
    elif score <= -3:
        signal = "STRONG SELL"
    elif score <= -1:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "score": score
    }