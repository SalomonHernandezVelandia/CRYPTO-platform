import plotly.graph_objects as go       # go significa graph_objects
import pandas as pd



# Función que crea toda la gráfica principal.
def plot_price_chart(df, peak_x, peak_y, valley_x, valley_y, avg_peak, avg_valley, trades, trend, signal=None, show_funding=True):
    fig = go.Figure()                   # Crea una figura vacía, todo se añade aqui

    # Volumen
    fig.add_trace(go.Bar(               # Añade barras
        x=df.index,                     # Eje X = fechas
        y=df["volume"],
        name="Volumen",                 # Nombre en leyenda
        opacity=0.15,                   # Transparencia
        yaxis="y2"                      # Usa segundo eje Y, Porque volumen tiene escala distinta.
    ))

    # VELAS (por defecto visibles)
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Velas",
        increasing=dict(
            line=dict(color='#16C784', width=1),
            fillcolor='#16C784'
        ),
        decreasing=dict(
            line=dict(color='#EA3943', width=1),
            fillcolor='#EA3943'
        ),
        visible=True                        # Visible por defecto.
    ))

    # LINEA (oculta por defecto)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["close"],
        mode='lines',                       # Solo líneas.
        name='Precio (línea)',
        line=dict(color='white', width=2),
        visible='legendonly'                # Oculta inicialmente.
    ))

    # EMA 13 (rápida)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ema_13"],
        mode='lines',
        name='EMA 13',
        line=dict(color='yellow', width=1, dash='dot'),         # Línea punteada.
    ))

    # EMA 48 (media)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ema_48"],
        mode='lines',
        name='EMA 48',
        line=dict(color='purple', width=2, dash='dash'),        # Línea segmentada.
    ))

    # EMA 200 (lenta)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ema_200"],
        mode='lines',
        name='EMA 200',
        line=dict(color='#8B0000', width=3, dash='longdash'),   # Línea larga segmentada.
    ))

    # VWAP
    fig.add_trace(go.Scatter(x=df.index, y=df["vwap"], name="VWAP", line=dict(color='orange', width=3)))

    # Swings
    fig.add_trace(go.Scatter(x=peak_x, y=peak_y, mode='markers', marker=dict(color='green'), name='Venta'))
    fig.add_trace(go.Scatter(x=valley_x, y=valley_y, mode='markers', marker=dict(color='red'), name='Compra'))

    # Trades
    first_trade = True
    USER_COLORS = {
        "SALOMON": "#FFD700",   # dorado brillante
        "LAURA": "#C77DFF",     # morado brillante
    }

    for trade in trades:
        trade_date = pd.to_datetime(trade["date"])
        trade_price = trade["price"]
        trade_user = trade.get("user", "USER")

        if trade_date < df.index.min() or trade_date > df.index.max():
            continue

        # =========================
        # COLOR SEGÚN USUARIO
        # =========================
        trade_color = USER_COLORS.get(
            trade_user.upper(),
            "#00E5FF"   # color default si aparece otro usuario
        )

        fig.add_trace(go.Scatter(
            x=[trade_date],
            y=[trade_price],

            mode='markers+text',

            text=[trade_user],
            textposition="top center",

            marker=dict(
                color=trade_color,
                size=18,

                line=dict(
                    color='white',
                    width=2
                ),

                symbol='diamond'
            ),

            textfont=dict(
                color=trade_color,
                size=12
            ),

            name='Entradas',
            showlegend=first_trade
        ))

        first_trade = False

        # Línea vertical
        fig.add_vline(
            x=trade_date,
            line_dash="dash",
            line_color=trade_color,
            line_width=2,
            opacity=0.9
        )

        # Línea horizontal
        fig.add_hline(
            y=trade_price,
            line_dash="dot",
            line_color=trade_color,
            line_width=2,
            opacity=0.8
        )

    # Funding
    if show_funding and "fundingRate" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["fundingRate"],
            mode='lines',
            name='Funding Rate',
            line=dict(color='cyan', width=1),
            yaxis="y3"                                                  # Tercer eje Y.
        ))

    # Levels
    if avg_peak:
        fig.add_hline(y=avg_peak, line_dash="dash", line_color="green")
    if avg_valley:
        fig.add_hline(y=avg_valley, line_dash="dash", line_color="red")

    # Zona
    if avg_peak is not None and avg_valley is not None:
        # COLOR SEGÚN SEÑAL
        if signal in ["BUY", "STRONG BUY"]:
            zone_color = "rgba(234,57,67,0.15)"   # rojo suave
        elif signal in ["SELL", "STRONG SELL"]:
            zone_color = "rgba(22,199,132,0.15)"  # verde suave
        else:
            zone_color = "rgba(255,255,255,0.08)" # blanco neutro
        # Crea rectángulo horizontal.
        fig.add_hrect(y0=avg_valley, y1=avg_peak, fillcolor=zone_color, opacity=1, layer="below", line_width=0,) 
        # líneas de referencia
        fig.add_hline(y=avg_peak, line_dash="dash", line_color="green")
        fig.add_hline(y=avg_valley, line_dash="dash", line_color="red")

    # Configurar apariencia.
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        xaxis=dict(type='date', rangeslider=dict(visible=True), showgrid=False),

        yaxis=dict(title="Precio"),
        yaxis2=dict(title="Volumen", overlaying="y", side="right", showgrid=False),
        yaxis3=dict(title="Funding", overlaying="y", side="right", position=0.95, showgrid=False),

        xaxis_title="Fecha"
    )

    return fig
    



# Crea gráfica del libro de órdenes.
def plot_orderbook_chart(bid_prices, bid_qty, ask_prices, ask_qty):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=bid_prices,                   # Compradores
        y=bid_qty,
        mode='lines',
        name='Bids',
        line=dict(color='green')
    ))

    fig.add_trace(go.Scatter(
        x=ask_prices,                   # Vendedores
        y=ask_qty,
        mode='lines',
        name='Asks',
        line=dict(color='red')
    ))

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        xaxis_title="Precio",
        xaxis_rangeslider_visible=False,
        bargap=0.05,
        yaxis_title="Volumen acumulado"
    )

    return fig