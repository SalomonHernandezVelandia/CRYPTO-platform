import numpy as np


def weighted_average(values, weights):
    if len(values) == 0:
        return None
    return np.sum(np.array(values) * np.array(weights)) / np.sum(weights)



def compute_weighted_levels(peak_y, valley_y, window, market_context, current_trend):
    # -------------------------------
    # Ventana dinámica
    # -------------------------------
    recent_peaks = peak_y[-window:] if len(peak_y) >= window else peak_y
    recent_valleys = valley_y[-window:] if len(valley_y) >= window else valley_y

    # -------------------------------
    # Pesos según contexto
    # -------------------------------
    if market_context == "ranging":
        valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
        peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))
    elif market_context == "trending":
        if current_trend == "Bullish":
            valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
            peak_weights = np.linspace(0.5, 1.0, len(recent_peaks))
        else:
            peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))
            valley_weights = np.linspace(0.5, 1.0, len(recent_valleys))
    elif market_context == "volatile":
        valley_weights = np.linspace(0.7, 1.0, len(recent_valleys))
        peak_weights = np.linspace(0.7, 1.0, len(recent_peaks))
    else:
        valley_weights = np.ones(len(recent_valleys))
        peak_weights = np.ones(len(recent_peaks))

    # -------------------------------
    # Resultado
    # -------------------------------
    avg_peak = weighted_average(recent_peaks, peak_weights) if len(recent_peaks) > 0 else None
    avg_valley = weighted_average(recent_valleys, valley_weights) if len(recent_valleys) > 0 else None

    return avg_peak, avg_valley