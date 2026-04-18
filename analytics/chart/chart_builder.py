import plotly.graph_objects as go

def build_chart(df, avg_peak, avg_valley, trend):

    fig = go.Figure()

    # -----------------------
    # 📊 VOLUMEN (TRANSPARENTE)
    # -----------------------
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["volume"],
        name="Volumen",
        opacity=0.30,   # 🔥 MÁS TRANSPARENCIA
        marker=dict(color="gray"),
        yaxis="y2"
    ))

    # ---------------------------
    # 📈 PRECIO
    # ---------------------------
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["close"],
        mode='lines',
        name='Precio',
        line=dict(color='white', width=3)
    ))

    # ---------------------------
    # 📊 MA20 / MA50
    # ---------------------------
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ma_20"],
        name="MA 20",
        line=dict(color='yellow', dash='dot')
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ma_50"],
        name="MA 50",
        line=dict(color='magenta', dash='dash')
    ))

    # ---------------------------
    # 📈 VWAP
    # ---------------------------
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["vwap"],
        name="VWAP",
        line=dict(color='orange')
    ))

    # ---------------------------
    # 🎯 ZONA VALLEY / PEAK
    # ---------------------------
    if avg_peak is not None and avg_valley is not None:

        zone_color = "rgba(0,255,0,0.15)" if trend == "Bullish" else "rgba(255,0,0,0.15)"

        fig.add_hrect(
            y0=avg_valley,
            y1=avg_peak,
            fillcolor=zone_color,
            opacity=0.12,
            line_width=0
        )

        fig.add_hline(y=avg_peak, line_dash="dash", line_color="green")
        fig.add_hline(y=avg_valley, line_dash="dash", line_color="red")

    # ---------------------------
    # 🎨 LAYOUT (ESTO ES LO QUE TE FALTABA)
    # ---------------------------
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),

        xaxis=dict(rangeslider=dict(visible=False)),

        yaxis=dict(
            title="Precio"
        ),

        yaxis2=dict(
            title="Volumen",
            overlaying="y",
            side="right",
            showgrid=False
        )
    )

    return fig