import numpy as np


def normalize_orderbook(orderbook):
    bids = orderbook.get("bids", [])
    asks = orderbook.get("asks", [])

    # convertir a float
    bids = [(float(p), float(q)) for p, q in bids]
    asks = [(float(p), float(q)) for p, q in asks]

    # ordenar correctamente
    bids = sorted(bids, key=lambda x: x[0], reverse=True)
    asks = sorted(asks, key=lambda x: x[0])

    return bids, asks



def compute_orderbook_metrics(bids, asks):
    bid_volume = sum(q for _, q in bids)
    ask_volume = sum(q for _, q in asks)

    imbalance = (
        bid_volume / (bid_volume + ask_volume)
        if (bid_volume + ask_volume) > 0 else 0
    )

    best_bid = bids[0][0] if bids else None
    best_ask = asks[0][0] if asks else None

    return {
        "bid_volume": bid_volume,
        "ask_volume": ask_volume,
        "imbalance": imbalance,
        "best_bid": best_bid,
        "best_ask": best_ask
    }



def compute_depth(bids, asks):
    bid_prices = [p for p, q in bids]
    bid_qty = np.cumsum([q for _, q in bids])

    ask_prices = [p for p, q in asks]
    ask_qty = np.cumsum([q for _, q in asks])

    return bid_prices, bid_qty, ask_prices, ask_qty