import numpy as np
from scipy.signal import find_peaks                                         # Detecta automáticamente máximos locales.



# Para la sensibilidad de detección
def get_trade_swings(df, prominence=0.05):                                  # prominese para qué tan importante debe ser un pico, entre mas pequeño Detecta MUCHOS swings.
    prices = df["close"].values                                             # (values) para convertir a NumPy array.
    
    peaks, _ = find_peaks(prices, prominence=prominence * np.mean(prices))      # Detectar picos, busca maximos locales. (_ Porque ignoras las propiedades, solo se quieren los indices)
    valleys, _ = find_peaks(-prices, prominence=prominence * np.mean(prices))

    events = [(p, "peak") for p in peaks] + [(v, "valley") for v in valleys]    # Construye lista combinada.
    events = sorted(events, key=lambda x: x[0])                                 # ORDENAR EVENTOS Porque peaks y valleys están mezclados.

    filtered = []
    last_type = None
    for idx, typ in events:                                                 # Recorrer eventos
        if typ != last_type:                                                # Si cambioa el tipo entonces se agrega
            filtered.append((idx, typ))
            last_type = typ
        else:                                                               # Si hay 2 tipos seguidos
            prev_idx, _ = filtered[-1]                                      # Toma el anterior, ultimo elemento
            if typ == "peak":
                if prices[idx] > prices[prev_idx]:                          # Quedarse con el mas alto pico
                    filtered[-1] = (idx, typ)
            elif typ == "valley":
                if prices[idx] < prices[prev_idx]:                          # Quedarse con el valle mas bajo
                    filtered[-1] = (idx, typ)

    return filtered




# Convierte índices → coordenadas reales.
def extract_swing_points(df, swings):
    peak_x, peak_y, valley_x, valley_y = [], [], [], []

    for idx, typ in swings:                                 # Recorrer los swings
        if typ == "peak":
            peak_x.append(df.index[idx])                    # Si es pico, añade la fecha
            peak_y.append(df["close"].iloc[idx])
        else:
            valley_x.append(df.index[idx])
            valley_y.append(df["close"].iloc[idx])

    return peak_x, peak_y, valley_x, valley_y