import pandas as pd


# =========================================
# HELPERS
def candle_size(candle):                            # Calcula el tamaño del cuerpo de una vela.
    return abs(candle["close"] - candle["open"])


def is_green(candle):                               # Detecta si la vela es alcista.                                 
    return candle["close"] > candle["open"]


def is_red(candle):                                 # Detecta si la vela es bajista.
    return candle["close"] < candle["open"]



# =========================================
# WICKS (Analizar mechas)
def lower_wick(candle):                             # Calcula la mecha inferior.
    body_low = min(candle["open"], candle["close"])
    return body_low - candle["low"]


def upper_wick(candle):                             # Calcula la mecha superior.
    body_high = max(candle["open"], candle["close"])
    return candle["high"] - body_high



# =========================================
# EXPLOSIVE SCORE (Calcula que tan explosiva es una vela en comparacion a otra)
def explosive_score(current_size, previous_size):
    if previous_size == 0:                  # proteccion division en cero
        return 0

    ratio = current_size / previous_size
    if ratio >= 7:
        return "💥 EXTREMA"
    elif ratio >= 5:
        return "🚀 MUY ALTA"
    elif ratio >= 3:
        return "⚡ ALTA"
    
    return "NORMAL"




# =========================================
# MAIN DETECTOR
# =========================================
def detect_rapid_reversal(df, trend):
    if len(df) < 5:                                 # Maximo de 5 velas
        return None

    c1 = df.iloc[-5]                                # Vela mas antigua
    c2 = df.iloc[-4]
    c3 = df.iloc[-3]
    c4 = df.iloc[-2]
    c5 = df.iloc[-1]

    # =========================================
    # CONDITION 1 ---> Engulfing Pattern
    prev_size = candle_size(c4)                     # Tamaño vela anterior
    curr_size = candle_size(c5)                     # Tamaño vela actual

    bullish_engulf = (                              # BAJISTA -> REVERSAL ALCISTA
        trend == "Bearish" and
        is_red(c4) and
        is_green(c5) and
        curr_size >= prev_size * 5
    )

    bearish_engulf = (                              # ALCISTA -> REVERSAL BAJISTA
        trend == "Bullish" and
        is_green(c4) and
        is_red(c5) and
        curr_size >= prev_size * 5
    )

    if bullish_engulf or bearish_engulf:
        movement = (abs(c5["close"] - c5["open"]) / c5["open"]) * 100
        return {
            "pattern": "ENGULFING PATTERN",
            "movement": movement,
            "explosive": explosive_score(curr_size, prev_size)
        }

    # =====================================
    # CONDITION 2
    red_sequence = (
        is_red(c1) and
        is_red(c2) and
        is_red(c3) and
        is_green(c4)
    )

    green_sequence = (
        is_green(c1) and
        is_green(c2) and
        is_green(c3) and
        is_red(c4)
    )

    if red_sequence:
        total_prev = (candle_size(c1) + candle_size(c2) + candle_size(c3))

        if candle_size(c4) >= total_prev * 0.9:
            movement = (candle_size(c4) / c4["open"]) * 100
            return {
                "pattern": "EXHAUSTION REVERSAL",
                "movement": movement,
                "explosive": "💥 EXTREMA"
            }

    if green_sequence:
        total_prev = (candle_size(c1) + candle_size(c2) + candle_size(c3))

        if candle_size(c4) >= total_prev * 0.9:
            movement = (candle_size(c4) / c4["open"]) * 100
            return {
                "pattern": "SHRINKING CANDLES",
                "movement": movement,
                "explosive": "💥 EXTREMA"
            }

    # =====================================
    # CONDITION 3
    bullish_shift = (
        trend == "Bearish" and
        is_red(c3) and
        is_red(c4) and
        is_green(c5) and
        candle_size(c5) >
        (candle_size(c3) + candle_size(c4))
    )

    bearish_shift = (
        trend == "Bullish" and
        is_green(c3) and
        is_green(c4) and
        is_red(c5) and
        candle_size(c5) >
        (candle_size(c3) + candle_size(c4))
    )

    if bullish_shift or bearish_shift:
        movement = (candle_size(c5) / c5["open"]) * 100
        return {
            "pattern": "MOMENTUM SHIFT",
            "movement": movement,
            "explosive": "🚀 MUY ALTA"
        }
    
    
    # =====================================
    # CONDITION 4 - PINBAR REVERSAL
    pinbar = df.iloc[-2]
    confirm = df.iloc[-1]
    pinbar_body = candle_size(pinbar)
    lower_shadow = lower_wick(pinbar)
    upper_shadow = upper_wick(pinbar)

    # BULLISH PINBAR
    bullish_pinbar = (
        trend == "Bearish" and
        is_green(pinbar) and
        lower_shadow >= pinbar_body * 5 and
        is_green(confirm) and
        candle_size(confirm) >= pinbar_body * 0.8
    )

    # BEARISH PINBAR
    bearish_pinbar = (
        trend == "Bullish" and
        is_red(pinbar) and
        upper_shadow >= pinbar_body * 5 and
        is_red(confirm) and
        candle_size(confirm) >= pinbar_body * 0.8
    )

    if bullish_pinbar:
        movement = (candle_size(confirm) / confirm["open"]) * 100

        return {
            "pattern": "BULLISH PINBAR",
            "movement": movement,
            "explosive": "⚡ REVERSAL",
            "message": "🟢 POSIBLE TENDENCIA ALCISTA PINBAR"
        }

    if bearish_pinbar:
        movement = (candle_size(confirm) / confirm["open"]) * 100

        return {
            "pattern": "BEARISH PINBAR",
            "movement": movement,
            "explosive": "⚡ REVERSAL",
            "message": "🔴 POSIBLE TENDENCIA BAJISTA PINBAR"
        }
    

    # =====================================
    # CONDITION 5 - 3 BAR CONTINUATION
    # Últimas 3 velas reales
    cont_1 = df.iloc[-3]
    cont_2 = df.iloc[-2]
    cont_3 = df.iloc[-1]

    c1_size = candle_size(cont_1)
    c2_size = candle_size(cont_2)
    c3_size = candle_size(cont_3)

    # BULLISH CONTINUATION
    bullish_continuation = (
        trend == "Bullish" and
        is_green(cont_1) and
        is_red(cont_2) and
        c2_size <= c1_size / 3 and
        is_green(cont_3) and
        c3_size >= c2_size * 3
    )

    # BEARISH CONTINUATION
    bearish_continuation = (
        trend == "Bearish" and
        is_red(cont_1) and
        is_green(cont_2) and
        c2_size <= c1_size / 3 and
        is_red(cont_3) and
        c3_size >= c2_size * 3
    )

    if bullish_continuation:
        movement = (c3_size / cont_3["open"]) * 100
        explosive_ratio = c3_size / c2_size
        return {
            "pattern": "3 BAR BULLISH CONTINUATION",
            "movement": movement,
            "explosive": f"{explosive_ratio:.1f}x",
            "message": "🟢 CONTINUACIÓN DE TENDENCIA ALCISTA"
        }

    if bearish_continuation:
        movement = (c3_size / cont_3["open"]) * 100
        explosive_ratio = c3_size / c2_size
        return {
            "pattern": "3 BAR BEARISH CONTINUATION",
            "movement": movement,
            "explosive": f"{explosive_ratio:.1f}x",
            "message": "🔴 CONTINUACIÓN DE TENDENCIA BAJISTA"
        }
    
    return None