# Devuelve el contexto del mercado, si es fuerte, lateral o caotico
def get_market_context(df):
    current_volatility = df["volatility"].iloc[-1]
    current_range = df["range"].iloc[-1]

    if current_volatility > df["volatility"].mean() * 1.5:
        return "volatile"
    elif current_range < df["range"].mean() * 0.8:
        return "ranging"
    else:
        return "trending"



# En futuros perpetuos: longs pagan shorts o viceversa
def get_funding_bias(funding_rate):
    if funding_rate > 0.0001:       # Longs pagan.
        return "longs_paying"
    elif funding_rate < -0.0001:    # Shorts pagan, demasiada gente bajista y en corto
        return "shorts_paying"
    else:
        return "neutral"
        