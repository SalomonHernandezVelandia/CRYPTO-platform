from analytics.backtesting.backtester import Backtester


def run_backtest(df, initial_capital=1000):
    """
    Ejecuta el backtesting sobre un DataFrame
    y devuelve métricas listas para usar.
    """

    bt = Backtester(df, initial_capital=initial_capital)
    results = bt.run()

    return results