import plotly.graph_objects as go
import pandas as pd


def plot_price_chart(
    df,
    peak_x,
    peak_y,
    valley_x,
    valley_y,
    avg_peak,
    avg_valley,
    trades,
    trend
):
    fig = go.Figure()

    # Volumen
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

    # Medias
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

    # Swings
    fig.add_trace(go.Scatter(x=peak_x, y=peak_y, mode='markers', marker=dict(color='green'), name='Venta'))
    fig.add_trace(go.Scatter(x=valley_x, y=valley_y, mode='markers', marker=dict(color='red'), name='Compra'))

    # Trades
    for trade in trades:
        trade_date = pd.to_datetime(trade["date"])
        trade_price = trade["price"]

        if trade_date < df.index.min() or trade_date > df.index.max():
            continue

        fig.add_trace(go.Scatter(
            x=[trade_date],
            y=[trade_price],
            mode='markers',
            marker=dict(color='purple', size=12),
            name='Entrada'
        ))

        fig.add_vline(x=trade_date, line_dash="dash", line_color="purple")
        fig.add_hline(y=trade_price, line_dash="dot", line_color="purple")

    # Funding
    if "fundingRate" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["fundingRate"],
            mode='lines',
            name='Funding Rate',
            line=dict(color='cyan', width=1),
            yaxis="y3"
        ))

    # Levels
    if avg_peak:
        fig.add_hline(y=avg_peak, line_dash="dash", line_color="green")

    if avg_valley:
        fig.add_hline(y=avg_valley, line_dash="dash", line_color="red")

    # Zona
    if avg_peak is not None and avg_valley is not None:
        zone_color = "rgba(0,255,0,0.2)" if trend == "Bullish" else "rgba(255,0,0,0.2)"
        fig.add_hrect(
            y0=avg_valley,
            y1=avg_peak,
            fillcolor=zone_color,
            opacity=0.1,
            layer="below",
            line_width=0,
        )

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        xaxis=dict(rangeslider=dict(visible=True)),

        yaxis=dict(title="Precio"),

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

    return fig


def plot_orderbook_chart(bid_prices, bid_qty, ask_prices, ask_qty):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=bid_prices,
        y=bid_qty,
        mode='lines',
        name='Bids',
        line=dict(color='green')
    ))

    fig.add_trace(go.Scatter(
        x=ask_prices,
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
        yaxis_title="Volumen acumulado"
    )

    return fig