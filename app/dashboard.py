import streamlit as st                                                      # Streamlit es el framework que convierte Python en una app web interactiva.
import pandas as pd
import os

from src.config.settings import SYMBOLS, TRADES
from src.config.paths import BASE_DIR, DATA_PATH

from analytics.backtesting.service import run_backtest
from analytics.pipeline import run_pipeline
from analytics.chart.plotters import plot_price_chart, plot_orderbook_chart

st.set_page_config(layout="wide")                                           # Hace app más ancha                       



# -------------------------------
# Cargar datos
# -------------------------------
@st.cache_data                                                              # Le dice a streamlit "No recalcules esto cada vez"
def load_funding(symbol):
    file_path = os.path.join(DATA_PATH, "funding_rate", f"{symbol}.csv")

    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path)
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time")

    return df



# -------------------------------
# UI
# -------------------------------
st.title("📊 Crypto Dashboard")                                         # Titulo del dashboard

col1, col2, col3, col4 = st.columns([1,1,1,1.2])                        # Divide la pantalla horizontalmente.

with col1:
    symbol = st.selectbox("Crypto", SYMBOLS)                            # Permite elegir la Cryptomoneda
with col2:
    interval = st.radio(                                                # Botones para timeframe.
        "Intervalo",
        ["15M", "1H", "4H", "Diario", "Semanal", "Mensual", "Anual"],
        index=1                                                         # Define el seleccionado por defecto (1H)
    )
with col3:                                                              # Controla cuánto histórico mostrar.
    range_option = st.radio(
        "Rango",
        ["1 Semana", "1 Mes", "1 Año", "Todo"],
        index=0
    )
with col4:
    prominence = st.slider("Sensibilidad", 0.01, 0.2, 0.01)             # Controla sensibilidad swings.
    window_swings = st.slider("Ventana", 5, 30, 10)



# -------------------------------
# Procesamiento
# -------------------------------
data = run_pipeline(symbol=symbol, interval=interval, range_option=range_option, prominence=prominence, window_swings=window_swings) # Ejecuta todo
df = data["df"]
signal_data = data["signal"]
current_trend = data["trend"]
momentum = df["momentum"].iloc[-1]                                                      # .iloc[-1] = Ultima fila

if momentum == "Bullish":
    st.markdown("<p style='color:lime;'>Momentum Alcista</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color:red;'>Momentum Bajista</p>", unsafe_allow_html=True)
market_context = data["context"]
current_funding = data["funding"]
ob_metrics = data["orderbook"]
imbalance = ob_metrics["imbalance"]
bid_prices, bid_qty, ask_prices, ask_qty = data["depth"]
peak_x, peak_y, valley_x, valley_y = data["swings"]
avg_peak, avg_valley = data["levels"]
signal = signal_data["signal"]
score = signal_data["score"]



# -------------------------------
# BACKTESTING
results = run_backtest(df)                                                              # Ejecuta simulación histórica, devolviendo retorno, sharpe, drawdown, etc


# -------------------------------
# Métricas
col1, col2, col3, col4 = st.columns(4)                                                  # Nuevas columnas
trend_label = "📈" if current_trend == "Bullish" else "📉"                             # Solo para definir emoji segun tendencia

valor_valley = f"{avg_valley:.6f} {trend_label}" if avg_valley else "N/A"               # Solo para definir el formato de texto
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
# RESULTADOS BACKTESTING
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
# GRÁFICA
# -------------------------------
st.subheader(f"{symbol} - {interval}")                              # Título gráfica.

fig = plot_price_chart(                                             # Realiza la grafica en plotters
    df=df,
    peak_x=peak_x,
    peak_y=peak_y,
    valley_x=valley_x,
    valley_y=valley_y,
    avg_peak=avg_peak,
    avg_valley=avg_valley,
    trades=TRADES.get(symbol, []),
    trend=current_trend,
    signal=signal
)
st.plotly_chart(fig, use_container_width=True)                      # Renderiza gráfica interactiva. Usa todo el ancho

st.subheader("📊 Order Book Depth")
fig_ob = plot_orderbook_chart(bid_prices,bid_qty,ask_prices,ask_qty)
st.plotly_chart(fig_ob, use_container_width=True)


# -------------------------------
# ORDER BOOK
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
# Tabla
# -------------------------------
st.write("Datos recientes:")
st.dataframe(df.tail(10).reset_index())