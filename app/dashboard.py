import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np
from scipy.signal import find_peaks

# 🔥 Hacer app más ancha
st.set_page_config(layout="wide")

# 📌 raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "binance")

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT",
    "DOGEUSDT", "ADAUSDT", "LINKUSDT",
    "AVAXUSDT", "HBARUSDT", "SHIBUSDT", "PEPEUSDT"
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
        "volume": "sum"
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

# -------------------------------
# 🎛️ UI
# -------------------------------
st.title("📊 Crypto Dashboard")

symbol = st.selectbox("Selecciona una criptomoneda", SYMBOLS)

col1, col2 = st.columns(2)

with col1:
    interval = st.radio(
        "Intervalo de tiempo",
        ["1H", "Diario", "Semanal", "Mensual", "Anual"]
    )

with col2:
    range_option = st.radio(
        "Rango de visualización",
        ["1 Mes", "1 Semana", "1 Año", "Todo"],
        index=0  # 👈 esto lo hace default
    )

prominence = st.slider("Sensibilidad de swings", 0.01, 0.2, 0.05)

# 🔥 NUEVO
window_swings = st.slider("Ventana swings", 5, 30, 10)

# -------------------------------
# 📊 Procesamiento
# -------------------------------
df = load_data(symbol)
df = filter_by_range(df, range_option)
df = resample_data(df, interval)

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
# 🔍 Swings
# -------------------------------
swings = get_trade_swings(df, prominence)

peak_y, valley_y, peak_x, valley_x = [], [], [], []

for idx, typ in swings:
    if typ == "peak":
        peak_x.append(df.index[idx])
        peak_y.append(df["close"].iloc[idx])
    else:
        valley_x.append(df.index[idx])
        valley_y.append(df["close"].iloc[idx])

# -------------------------------
# 📊 Promedios dinámicos
# -------------------------------
WINDOW_SWINGS = window_swings

recent_peaks = peak_y[-WINDOW_SWINGS:] if len(peak_y) >= WINDOW_SWINGS else peak_y
recent_valleys = valley_y[-WINDOW_SWINGS:] if len(valley_y) >= WINDOW_SWINGS else valley_y

avg_peak = np.mean(recent_peaks) if len(recent_peaks) > 0 else None
avg_valley = np.mean(recent_valleys) if len(recent_valleys) > 0 else None

# -------------------------------
# 📈 Métricas
# -------------------------------
col_left, col_right = st.columns(2)

valor_valley = f"{avg_valley:.6f}" if avg_valley else "N/A"
valor_peak = f"{avg_peak:.6f}" if avg_peak else "N/A"

with col_left:
    st.markdown(f"<h3 style='color:red;'>Compra: {valor_valley}</h3>", unsafe_allow_html=True)

with col_right:
    st.markdown(f"<h3 style='color:green; text-align:right;'>Venta: {valor_peak}</h3>", unsafe_allow_html=True)

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

# Líneas promedio
if avg_peak:
    fig.add_hline(y=avg_peak, line_dash="dash", line_color="green")

if avg_valley:
    fig.add_hline(y=avg_valley, line_dash="dash", line_color="red")

# -------------------------------
# 🔵 ZONA ENTRE COMPRA Y VENTA
# -------------------------------
if avg_peak is not None and avg_valley is not None:
    fig.add_hrect(
        y0=avg_valley,
        y1=avg_peak,
        fillcolor="gold",
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

    xaxis_title="Fecha"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📋 Tabla
# -------------------------------
st.write("Datos recientes:")
st.dataframe(df.tail(10).reset_index())