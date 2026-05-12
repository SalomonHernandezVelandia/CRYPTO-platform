from analytics.chart.plotters import plot_price_chart

def build_chart(df, avg_peak, avg_valley, trend, signal):
    fig = plot_price_chart(
        df=df,
        peak_x=[],
        peak_y=[],
        valley_x=[],
        valley_y=[],
        avg_peak=avg_peak,
        avg_valley=avg_valley,
        trades=[],
        trend=trend,
        signal=signal,
        show_funding=False
    )

    # Ajustes específicos para Telegram, Desactiva esto:<img src="https://i.imgur.com/eB2wL5N.png" width="500"> el mini-slider inferior que ocupa espacio imnecesario
    fig.update_layout(
        xaxis_rangeslider_visible=False
    )

    return fig