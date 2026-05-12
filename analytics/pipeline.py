import os
import pandas as pd

from src.api.binance.client import get_order_book
from src.config.paths import DATA_PATH

from analytics.indicators.market_indicators import add_indicators
from analytics.indicators.swings import get_trade_swings, extract_swing_points
from analytics.indicators.weighted_levels import compute_weighted_levels
from analytics.indicators.orderbook import normalize_orderbook, compute_orderbook_metrics, compute_depth
from analytics.signals.market_context import get_market_context
from analytics.signals.signal_engine import compute_signal


# -------------------------------
# DATA LOADING    
# -------------------------------
def load_data(symbol):
    file_path = os.path.join(DATA_PATH, f"{symbol}.csv")
    df = pd.read_csv(file_path)

    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.sort_values("open_time")
    df = df.set_index("open_time")

    return df


# Carga CSV de funding.
def load_funding(symbol):
    file_path = os.path.join(DATA_PATH, "funding_rate", f"{symbol}.csv")
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time")

    return df



# -------------------------------
# TRANSFORMATIONS
def resample_data(df, interval):
    if interval == "15M":           # 15M = datos originales
        return df

    rule_map = {
        "1H": "1h",
        "4H": "4h",
        "Diario": "D",
        "Semanal": "W",
        "Mensual": "M",
        "Anual": "Y"
    }
    rule = rule_map.get(interval)   # Obtener regla

    if rule is None:                # Proteccion si no existe
        return df

    df = df.resample(rule).agg({    # Agrupa las velas segun el intervalo
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "fundingRate": "mean"
    })
    df = df.dropna()                # Elimina velas incompletas, evita velas corruptas

    return df


# -------------------------------
# FILTRA RANGO TEMPORAL
def filter_by_range(df, range_option):
    end_date = df.index.max()                           # Ultima fecha

    if range_option == "1 Semana":
        start_date = end_date - pd.Timedelta(days=7)
    elif range_option == "1 Mes":
        start_date = end_date - pd.Timedelta(days=30)
    elif range_option == "1 Año":
        start_date = end_date - pd.Timedelta(days=365)
    else:
        return df

    return df[df.index >= start_date]



# -------------------------------
# MAIN PIPELINE
# -------------------------------
def run_pipeline(symbol, interval, range_option, prominence, window_swings):
    # 1. Data
    df = load_data(symbol)
    funding_df = load_funding(symbol)

    if funding_df is not None:
        df = df.merge(funding_df, left_index=True, right_index=True, how="left")    # El merge() une funding con velas 
        df["fundingRate"] = df["fundingRate"].ffill()                               # Funding no cambia cada vela, entonces rellena espacios.

    # 2. Transform
    df = filter_by_range(df, range_option)                                          # Filtra el tiempo
    df = resample_data(df, interval)                                                # Transforma el time_frame

    # 3. Indicators
    df = add_indicators(df)                                                         # Agrega EMA, VWAP, volatilidad, momentum
    # NUEVAS VARIABLES (EMA)
    current_trend = df["trend"].iloc[-1]
    current_momentum = df["momentum"].iloc[-1]
    market_context = get_market_context(df)

    # 4. Orderbook
    orderbook = get_order_book(symbol, limit=100)
    bids, asks = normalize_orderbook(orderbook)
    ob_metrics = compute_orderbook_metrics(bids, asks)
    bid_prices, bid_qty, ask_prices, ask_qty = compute_depth(bids, asks)

    # 5. Swings
    swings = get_trade_swings(df, prominence)
    peak_x, peak_y, valley_x, valley_y = extract_swing_points(df, swings)

    # 6. Funding
    if "fundingRate" in df.columns and not df["fundingRate"].isna().all():
        current_funding = df["fundingRate"].iloc[-1]
    else:
        current_funding = 0

    # 7. Levels
    avg_peak, avg_valley = compute_weighted_levels(
        peak_y=peak_y,
        valley_y=valley_y,
        window=window_swings,
        market_context=market_context,
        current_trend=current_trend
    )

    # 8. Signal
    price = df["close"].iloc[-1]

    signal_data = compute_signal(
        price=price,
        vwap=df["vwap"].iloc[-1],
        trend=current_trend,
        momentum=current_momentum,
        funding=current_funding,
        imbalance=ob_metrics["imbalance"],
        avg_valley=avg_valley,
        avg_peak=avg_peak,
        market_context=market_context
    )

    return {
        "df": df,
        "signal": signal_data,
        "trend": current_trend,
        "context": market_context,
        "funding": current_funding,
        "orderbook": ob_metrics,
        "depth": (bid_prices, bid_qty, ask_prices, ask_qty),
        "swings": (peak_x, peak_y, valley_x, valley_y),
        "levels": (avg_peak, avg_valley)
    }