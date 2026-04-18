import numpy as np
from scipy.signal import find_peaks


def get_trade_swings(df, prominence=0.05):
    prices = df["close"].values
    
    peaks, _ = find_peaks(prices, prominence=prominence * np.mean(prices))
    valleys, _ = find_peaks(-prices, prominence=prominence * np.mean(prices))

    events = [(p, "peak") for p in peaks] + [(v, "valley") for v in valleys]
    events = sorted(events, key=lambda x: x[0])

    filtered = []
    last_type = None

    for idx, typ in events:
        if typ != last_type:
            filtered.append((idx, typ))
            last_type = typ
        else:
            prev_idx, _ = filtered[-1]
            if typ == "peak":
                if prices[idx] > prices[prev_idx]:
                    filtered[-1] = (idx, typ)
            elif typ == "valley":
                if prices[idx] < prices[prev_idx]:
                    filtered[-1] = (idx, typ)

    return filtered



def extract_swing_points(df, swings):
    peak_x, peak_y, valley_x, valley_y = [], [], [], []

    for idx, typ in swings:
        if typ == "peak":
            peak_x.append(df.index[idx])
            peak_y.append(df["close"].iloc[idx])
        else:
            valley_x.append(df.index[idx])
            valley_y.append(df["close"].iloc[idx])

    return peak_x, peak_y, valley_x, valley_y