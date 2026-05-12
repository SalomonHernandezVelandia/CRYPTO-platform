import pandas as pd
import numpy as np

class Backtester:

    def __init__(self, df, initial_capital=1000):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []


    def weighted_average(self, values, weights):
        if len(values) == 0:
            return None
        return np.sum(np.array(values) * np.array(weights)) / np.sum(weights)


    def compute_context(self):
        df = self.df
        df["ema_13"] = df["close"].ewm(span=13, adjust=False).mean()
        df["ema_48"] = df["close"].ewm(span=48, adjust=False).mean()
        df["ema_200"] = df["close"].ewm(span=200, adjust=False).mean()
        df["trend"] = np.where(df["ema_48"] > df["ema_200"], "bullish", "bearish")
        df["volatility"] = df["close"].rolling(20).std()
        df["range"] = df["high"].rolling(20).max() - df["low"].rolling(20).min()
        return df


    def get_context(self, row, df):
        vol_mean = df["volatility"].mean()
        range_mean = df["range"].mean()
        if row["volatility"] > vol_mean * 1.5:
            return "volatile"
        elif row["range"] < range_mean * 0.8:
            return "ranging"
        else:
            return "trending"


    def run(self):
        df = self.compute_context()
        if len(df) < 50:
            self.equity_curve = []
            self.final_value = self.initial_capital
            return self.results()
        equity_curve = []

        warmup = 220

        for i in range(warmup, len(df)):
            window = df.iloc[:i]
            current_price = df["close"].iloc[i]
            row = df.iloc[i]
            context = self.get_context(row, df)
            trend = row["trend"]
            closes = window["close"].values
            peaks = []
            valleys = []

            for j in range(1, len(closes)-1):
                if closes[j] > closes[j-1] and closes[j] > closes[j+1]:
                    peaks.append(closes[j])
                if closes[j] < closes[j-1] and closes[j] < closes[j+1]:
                    valleys.append(closes[j])

            recent_peaks = peaks[-10:]
            recent_valleys = valleys[-10:]

            if context == "ranging":
                peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))
                valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
            elif context == "trending":
                if trend == "bullish":
                    valley_weights = np.linspace(1.5, 1.0, len(recent_valleys))
                    peak_weights = np.linspace(0.5, 1.0, len(recent_peaks))
                else:
                    peak_weights = np.linspace(1.5, 1.0, len(recent_peaks))
                    valley_weights = np.linspace(0.5, 1.0, len(recent_valleys))
            else:
                peak_weights = np.linspace(0.7, 1.0, len(recent_peaks))
                valley_weights = np.linspace(0.7, 1.0, len(recent_valleys))

            avg_peak = self.weighted_average(recent_peaks, peak_weights) if len(recent_peaks) > 0 else None
            avg_valley = self.weighted_average(recent_valleys, valley_weights) if len(recent_valleys) > 0 else None

            # Trading logic
            if avg_valley and current_price < avg_valley and self.position == 0:
                self.position = self.capital / current_price
                self.capital = 0
                self.trades.append(("BUY", current_price, i))
            elif avg_peak and current_price > avg_peak and self.position > 0:
                self.capital = self.position * current_price
                self.position = 0
                self.trades.append(("SELL", current_price, i))

            equity = self.capital if self.position == 0 else self.position * current_price
            equity_curve.append(equity)

        self.equity_curve = equity_curve
        self.final_value = equity_curve[-1] if equity_curve else self.initial_capital
        return self.results()


    def results(self):
        if len(self.equity_curve) == 0:
            return {
                "final_value": self.initial_capital,
                "total_return": 0,
                "win_rate": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "total_trades": 0
            }

        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        if len(returns) == 0:
            sharpe = 0
        else:
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) != 0 else 0
        total_return = (self.final_value - self.initial_capital) / self.initial_capital
        win_trades = 0
        total_trades = len(self.trades) // 2

        for i in range(0, len(self.trades)-1, 2):
            buy = self.trades[i][1]
            sell = self.trades[i+1][1]
            if sell > buy:
                win_trades += 1

        win_rate = win_trades / total_trades if total_trades > 0 else 0
        max_drawdown = 0
        peak = self.equity_curve[0]

        for value in self.equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_drawdown:
                max_drawdown = dd
        sharpe = np.mean(returns) / np.std(returns) if np.std(returns) != 0 else 0

        return {
            "final_value": self.final_value,
            "total_return": total_return,
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe,
            "total_trades": total_trades
        }
