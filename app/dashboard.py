import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np
from scipy.signal import find_peaks
from analytics.backtesting.backtester import Backtester
from exchange_API.binance.client import get_order_book
from analytics.signals.signal_engine import compute_signal

# 🔥 Hacer app más ancha
st.set_page_config(layout="wide")

# 📌 raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "binance")

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT",
    "DOGEUSDT", "ADAUSDT", "LINKUSDT", "XMRUSDT",
    "AVAXUSDT", "HBARUSDT", "SHIBUSDT", "PEPEUSDT", "XLMUSDT"
]

# -------------------------------
# 📌 HISTORIAL DE TRADES
# -------------------------------
TRADES = {
    "BTCUSDT": [
        {"date": "2024-03-10 12:00", "price": 68250.123456},
        {"date": "2024-03-15 08:00", "price": 70120.654321},
    ],
    "ETHUSDT": [
        {"date": "2024-03-12 10:00", "price": 3450.123456},
    ],
    "HBARUSDT": [
        {"date": "2026-04-12 1:00", "price": 0.08707},
    ]
}

# -------------------------------
# 📥 Cargar datos
# -------------------------------
@st.cache_data
def load_data(symbol):
    file_path = os.path.join(DATA_PATH, f"{symbol}.csv")
    df = pd.read_csv(file_path)

    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.sort_values("open_time")
    df = df.set_index("open_time")

    return df

@st.cache_data
def load_funding(symbol):
    file_path = os.path.join(DATA_PATH, "funding_rate", f"{symbol}.csv")

    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time")

    return df



# -------------------------------
# 🔄 Resampling
# -------------------------------
def resample_data(df, interval):

    if interval == "1H":
        return df

    rule_map = {
        "Diario": "D",
        "Semanal": "W",
        "Mensual": "M",
        "Anual": "Y"
    }

    rule = rule_map.get(interval)

    df = df.resample(rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "fundingRate": "mean"   # 🔥 clave
    })

    return df

# -------------------------------
# ⏳ Filtro de rango
# -------------------------------
def filter_by_range(df, range_option):

    end_date = df.index.max()

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
# 🔥 SWINGS
# -------------------------------
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


def analyze_order_book(orderbook):

    bids = orderbook.get("bids", [])
    asks = orderbook.get("asks", [])

    # convertir a float
    bids = [(float(p), float(q)) for p, q in bids]
    asks = [(float(p), float(q)) for p, q in asks]

    # volumen total
    bid_volume = sum(q for _, q in bids)
    ask_volume = sum(q for _, q in asks)

    # imbalance
    imbalance = bid_volume / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0

    # mejores precios
    best_bid = bids[0][0] if bids else None
    best_ask = asks[0][0] if asks else None

    return {
        "bid_volume": bid_volume,
        "ask_volume": ask_volume,
        "imbalance": imbalance,
        "best_bid": best_bid,
        "best_ask": best_ask
    }


# -------------------------------
# 🎛️ UI
# -------------------------------
st.title("📊 Crypto Dashboard")

col1, col2, col3, col4 = st.columns([1,1,1,1.2])

with col1:
    symbol = st.selectbox("Crypto", SYMBOLS)

with col2:
    interval = st.radio(
        "Intervalo",
        ["1H", "Diario", "Semanal", "Mensual", "Anual"]
    )

with col3:
    range_option = st.radio(
        "Rango",
        ["1 Mes", "1 Semana", "1 Año", "Todo"],
        index=0
    )

with col4:
    prominence = st.slider("Sensibilidad", 0.01, 0.2, 0.05)
    window_swings = st.slider("Ventana", 5, 30, 10)


# -------------------------------
# 📊 Procesamiento
# -------------------------------
df = load_data(symbol)
funding_df = load_funding(symbol)

if funding_df is not None:
    df = df.merge(funding_df, left_index=True, right_index=True, how="left")
    df["fundingRate"] = df["fundingRate"].ffill()

df = filter_by_range(df, range_option)
df = resample_data(df, interval)

orderbook = get_order_book(symbol, limit=100)
ob_metrics = analyze_order_book(orderbook)

imbalance = ob_metrics["imbalance"]

bids = orderbook.get("bids", [])
asks = orderbook.get("asks", [])

bids = [(float(p), float(q)) for p, q in bids]
asks = [(float(p), float(q)) for p, q in asks]

# ordenar
bids = sorted(bids, key=lambda x: x[0], reverse=True)
asks = sorted(asks, key=lambda x: x[0])

# acumulado
bid_prices = [p for p, q in bids]
bid_qty = np.cumsum([q for _, q in bids])

ask_prices = [p for p, q in asks]
ask_qty = np.cumsum([q for _, q in asks])


# -------------------------------
# 🧪 BACKTESTING
# -------------------------------
bt = Backtester(df)
results = bt.run()

# -------------------------------
# 📊 VOLUMEN
# -------------------------------
df["vol_ma_20"] = df["volume"].rolling(20).mean()

# -------------------------------
# 📈 VWAP
# -------------------------------
df["cum_vol"] = df["volume"].cumsum()
df["cum_vol_price"] = (df["close"] * df["volume"]).cumsum()
df["vwap"] = df["cum_vol_price"] / df["cum_vol"]


# -------------------------------
# 📈 Medias móviles
# -------------------------------
df["ma_20"] = df["close"].rolling(20).mean()
df["ma_50"] = df["close"].rolling(50).mean()


# -------------------------------
# 📈 Tendencia (Trend)
# -------------------------------
df["trend"] = np.where(df["ma_20"] > df["ma_50"], "Bullish", "Bearish")

# tendencia actual
current_trend = df["trend"].iloc[-1]

# -------------------------------
# 🔍 Swings
# -------------------------------
swings = get_trade_swings(df, prominence)

# -------------------------------
# 🌍 Contexto de mercado
# -------------------------------

# volatilidad simple (no ATR)
df["volatility"] = df["close"].rolling(20).std()

# rango reciente
df["range"] = df["high"].rolling(20).max() - df["low"].rolling(20).min()

current_volatility = df["volatility"].iloc[-1]
current_range = df["range"].iloc[-1]

# lógica de contexto
if current_volatility > df["volatility"].mean() * 1.5:
    market_context = "volatile"

elif current_range < df["range"].mean() * 0.8:
    market_context = "ranging"

else:
    market_context = "trending"

peak_y, valley_y, peak_x, valley_x = [], [], [], []

for idx, typ in swings:
    if typ == "peak":
        peak_x.append(df.index[idx])
        peak_y.append(df["close"].iloc[idx])
    else:
        valley_x.append(df.index[idx])
        valley_y.append(df["close"].iloc[idx])


#----------------------
if "fundingRate" in df.columns and not df["fundingRate"].isna().all():
    current_funding = df["fundingRate"].iloc[-1]
else:
    current_funding = 0

if current_funding > 0.0001:
    funding_bias = "longs_paying"
elif current_funding < -0.0001:
    funding_bias = "shorts_paying"
else:
    funding_bias = "neutral"


# -------------------------------
# 📊 Promedios dinámicos
# -------------------------------
WINDOW_SWINGS = window_swings

recent_peaks = peak_y[-WINDOW_SWINGS:] if len(peak_y) >= WINDOW_SWINGS else peak_y
recent_valleys = valley_y[-WINDOW_SWINGS:] if len(valley_y) >= WINDOW_SWINGS else valley_y

# -------------------------------
# ⚖️ Promedios ponderados por tendencia
# -------------------------------

def weighted_average(values, weights):
    if len(values) == 0:
        return None
    return np.sum(np.array(values) * np.array(weights)) / np.sum(weights)

# -------------------------------
# ⚖️ Pesos con contexto de mercado
# -------------------------------

if market_context == "ranging":
    # en rango → tu estrategia funciona mejor
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
    # mercado peligroso → reducir impacto
    valley_weights = np.linspace(0.7, 1.0, len(recent_valleys))
    peak_weights = np.linspace(0.7, 1.0, len(recent_peaks))

# cálculo final
avg_peak = weighted_average(recent_peaks, peak_weights) if len(recent_peaks) > 0 else None
avg_valley = weighted_average(recent_valleys, valley_weights) if len(recent_valleys) > 0 else None



#=======================================
price = df["close"].iloc[-1]
signal_data = compute_signal(
    price=price,
    vwap=df["vwap"].iloc[-1],
    trend=current_trend,
    funding=current_funding,
    imbalance=imbalance,
    avg_valley=avg_valley,
    avg_peak=avg_peak
)
signal = signal_data["signal"]
score = signal_data["score"]



# -------------------------------
# 📈 Métricas
# -------------------------------
col1, col2, col3, col4 = st.columns(4)
trend_label = "📈" if current_trend == "Bullish" else "📉"

valor_valley = f"{avg_valley:.6f} {trend_label}" if avg_valley else "N/A"
valor_peak = f"{avg_peak:.6f} {trend_label}" if avg_peak else "N/A"
# 🟥 COMPRA
with col1:
    st.markdown(f"<h3 style='color:red;'>Compra: {valor_valley}</h3>", unsafe_allow_html=True)
    st.metric("Funding", f"{current_funding:.5f}")

# 📈 TREND
with col2:
    if current_trend == "Bullish":
        st.markdown("<h3 style='color:lime;'>📈 Alcista</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='color:red;'>📉 Bajista</h3>", unsafe_allow_html=True)

# 🌍 CONTEXTO
with col3:
    if market_context == "trending":
        st.markdown("<h3 style='color:cyan;'>Tendencial</h3>", unsafe_allow_html=True)
    elif market_context == "ranging":
        st.markdown("<h3 style='color:orange;'>Lateral</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='color:red;'>Volátil</h3>", unsafe_allow_html=True)

# 🟩 VENTA
with col4:
    st.markdown(
        f"<h3 style='color:lime; text-align:right;'>💰 Venta: {valor_peak}</h3>",
        unsafe_allow_html=True
    )


# -------------------------------
# 📊 RESULTADOS BACKTESTING
# -------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Retorno", f"{results['total_return']*100:.2f}%")

with col2:
    st.metric("Win Rate", f"{results['win_rate']*100:.2f}%")

with col3:
    st.metric("Drawdown", f"{results['max_drawdown']*100:.2f}%")

with col4:
    st.metric("Sharpe", f"{results['sharpe_ratio']:.2f}")

with col5:
    st.metric("Trades", results["total_trades"])


if signal == "STRONG BUY":
    st.success(f"🚀 {signal} (Score: {score})")

elif signal == "BUY":
    st.info(f"🟢 {signal} (Score: {score})")

elif signal == "SELL":
    st.warning(f"🟠 {signal} (Score: {score})")

elif signal == "STRONG SELL":
    st.error(f"🔴 {signal} (Score: {score})")

else:
    st.write(f"⚪ HOLD (Score: {score})")

# -------------------------------
# 📈 GRÁFICA
# -------------------------------
st.subheader(f"{symbol} - {interval}")

fig = go.Figure()

# volumen como barras (transparente)
fig.add_trace(go.Bar(
    x=df.index,
    y=df["volume"],
    name="Volumen",
    opacity=0.15,
    yaxis="y2"
))

# Precio
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["close"],
    mode='lines',
    name='Precio',
    line=dict(color='white', width=3)
))

# MA
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["ma_20"],
    mode='lines',
    name='MA 20',
    line=dict(color='yellow', width=2, dash='dot'),
    opacity=0.7
))
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["ma_50"],
    mode='lines',
    name='MA 50',
    line=dict(color='magenta', width=2, dash='dash'),
    opacity=0.7
))

# -------------------------------
# 📈 Trend visual (fondo)
# -------------------------------
Bullish_mask = df["trend"] == "Bullish"

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["close"],
    mode='lines',
    name='Precio',
    line=dict(color='white', width=3)
))

# VWAP
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["vwap"],
    mode='lines',
    name='VWAP',
    line=dict(color='orange', width=1.5)
))

# Picos y valles
fig.add_trace(go.Scatter(x=peak_x, y=peak_y, mode='markers', marker=dict(color='green'), name='Venta'))
fig.add_trace(go.Scatter(x=valley_x, y=valley_y, mode='markers', marker=dict(color='red'), name='Compra'))

# -------------------------------
# 🟣 TRADES GUARDADOS
# -------------------------------
symbol_trades = TRADES.get(symbol, [])

for trade in symbol_trades:

    trade_date = pd.to_datetime(trade["date"])
    trade_price = trade["price"]

    if trade_date < df.index.min() or trade_date > df.index.max():
        continue

    # punto
    fig.add_trace(go.Scatter(
        x=[trade_date],
        y=[trade_price],
        mode='markers',
        marker=dict(
            color='purple',
            size=12,
            symbol='circle',
            line=dict(color='white', width=2)
        ),
        name='Entrada'
    ))

    # línea vertical
    fig.add_vline(
        x=trade_date,
        line_dash="dash",
        line_color="purple",
        line_width=1
    )

    # línea horizontal
    fig.add_hline(
        y=trade_price,
        line_dash="dot",
        line_color="purple"
    )

if "fundingRate" in df.columns:
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["fundingRate"],
        mode='lines',
        name='Funding Rate',
        line=dict(color='cyan', width=1),
        yaxis="y3"
    ))

# Líneas promedio
if avg_peak:
    fig.add_hline(y=avg_peak, line_dash="dash", line_color="green")

if avg_valley:
    fig.add_hline(y=avg_valley, line_dash="dash", line_color="red")

# -------------------------------
# 🔵 ZONA ENTRE COMPRA Y VENTA
# -------------------------------
if avg_peak is not None and avg_valley is not None:
    zone_color = "rgba(0,255,0,0.2)" if current_trend == "Bullish" else "rgba(255,0,0,0.2)"
    fig.add_hrect(
        y0=avg_valley,
        y1=avg_peak,
        fillcolor=zone_color,
        opacity=0.1,
        layer="below",
        line_width=0,
    )

# Layout
fig.update_layout(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    xaxis=dict(rangeslider=dict(visible=True)),
    
    yaxis=dict(
        title="Precio"
    ),

    yaxis2=dict(
        title="Volumen",
        overlaying="y",
        side="right",
        showgrid=False
    ),

    yaxis3=dict(
        title="Funding",
        overlaying="y",
        side="right",
        position=0.95,
        showgrid=False
    ),

    xaxis_title="Fecha"
)


st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Order Book Depth")

fig_ob = go.Figure()

fig_ob.add_trace(go.Scatter(
    x=bid_prices,
    y=bid_qty,
    mode='lines',
    name='Bids',
    line=dict(color='green')
))

fig_ob.add_trace(go.Scatter(
    x=ask_prices,
    y=ask_qty,
    mode='lines',
    name='Asks',
    line=dict(color='red')
))

fig_ob.update_layout(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    xaxis_title="Precio",
    yaxis_title="Volumen acumulado"
)

st.plotly_chart(fig_ob, use_container_width=True)
fig.write_image("chart.png")


# -------------------------------
# 📊 ORDER BOOK
# -------------------------------
col_ob1, col_ob2, col_ob3 = st.columns(3)

with col_ob1:
    st.metric("Bid Volume", f"{ob_metrics['bid_volume']:.2f}")

with col_ob2:
    st.metric("Ask Volume", f"{ob_metrics['ask_volume']:.2f}")

with col_ob3:
    st.metric("Imbalance", f"{imbalance:.2f}")

if imbalance > 0.55:
    st.success("🟢 Presión compradora (posible soporte)")
elif imbalance < 0.45:
    st.error("🔴 Presión vendedora (posible resistencia)")
else:
    st.warning("🟡 Mercado balanceado")

# -------------------------------
# 📋 Tabla
# -------------------------------
st.write("Datos recientes:")
st.dataframe(df.tail(10).reset_index())