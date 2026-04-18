def get_market_context(df):
    current_volatility = df["volatility"].iloc[-1]
    current_range = df["range"].iloc[-1]

    if current_volatility > df["volatility"].mean() * 1.5:
        return "volatile"
    elif current_range < df["range"].mean() * 0.8:
        return "ranging"
    else:
        return "trending"



def get_funding_bias(funding_rate):
    if funding_rate > 0.0001:
        return "longs_paying"
    elif funding_rate < -0.0001:
        return "shorts_paying"
    else:
        return "neutral"
        