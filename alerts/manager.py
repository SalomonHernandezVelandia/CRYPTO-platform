def build_signal_message(symbol, data):
    peak = f"{data['w_peak']:.5f}" if data["w_peak"] else "N/A"         # Valores promedios de compra
    valley = f"{data['w_valley']:.5f}" if data["w_valley"] else "N/A"   # Valores promedios de venta

    trend_emoji = "📈" if data["trend"] == "Bullish" else "📉"

    # Verificar el contexto del mercado
    if data["context"] == "trending":
        context_emoji = "Tendencial"
    elif data["context"] == "ranging":
        context_emoji = "Lateral"
    else:
        context_emoji = "Volátil"

    funding = f"{data['funding']:.5f}"                                  # Formatea el valor del funding


    # ====== AQUI SE CONSTRUYE TODO EL MENSAJE ================================
    message = f"""
🪙 *{symbol}* ==> Precio: {data['price']:.5f}
                                VWAP: {data['vwap_week']:.5f}

Buy: {valley}    |    Sell: {peak}
🔄 Trades: {data['trades_week']}
{trend_emoji} Trend: {data['trend']}
🌍 Contexto Mercado: {context_emoji}
💰 Funding: {funding}
"""

    return message