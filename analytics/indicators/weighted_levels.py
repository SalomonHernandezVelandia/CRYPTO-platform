import numpy as np


# Función para calcular un promedio ponderado, no todos tendran el mismo nivel de importancia.
def weighted_average(values, weights):
    if len(values) == 0:
        return None
    return np.sum(np.array(values) * np.array(weights)) / np.sum(weights)



# Funcion principal que calcula la zona de compra y venta
def compute_weighted_levels(peak_y, valley_y, window, market_context, current_trend):
    # -------------------------------
    # Ventana dinámica
    # -------------------------------
    recent_peaks = peak_y[-window:] if len(peak_y) >= window else peak_y            # toma los ultimos n elementos
    recent_valleys = valley_y[-window:] if len(valley_y) >= window else valley_y

    # -------------------------------
    # Pesos según contexto
    # -------------------------------
    if market_context == "ranging":                                                 # Los swings mas recientes pesan mas, los mas antiguos pesan menos
        valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
        peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))
    elif market_context == "trending":
        if current_trend == "Bullish":                                              # En alcistas importan más los soportes, los retrocesos suelen respetarse
            valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
            peak_weights = np.linspace(0.5, 1.0, len(recent_peaks))
        else:                                                                       # En bajadas las resistencias importan mucho, valles menos importantes soportes suelen romperse
            peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))
            valley_weights = np.linspace(0.5, 1.0, len(recent_valleys))
    elif market_context == "volatile":                                              # Los swings son menos confiables, hay mucho ruido
        valley_weights = np.linspace(0.7, 1.0, len(recent_valleys))
        peak_weights = np.linspace(0.7, 1.0, len(recent_peaks))
    else:                                                                           # Y por default todos pesan igual.
        valley_weights = np.ones(len(recent_valleys))
        peak_weights = np.ones(len(recent_peaks))

    # -------------------------------
    # Resultado
    # -------------------------------
    avg_peak = weighted_average(recent_peaks, peak_weights) if len(recent_peaks) > 0 else None          # Calculo de zona promedio de soportes
    avg_valley = weighted_average(recent_valleys, valley_weights) if len(recent_valleys) > 0 else None

    return avg_peak, avg_valley