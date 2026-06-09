import requests
import pandas as pd

def fetch_binance(symbol="BTCUSDT", interval="1d", limit=500):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": min(limit, 1000)}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()
    df = pd.DataFrame(raw, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","quote_volume","trades",
        "taker_buy_base","taker_buy_quote","ignore"
    ])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    for col in ["open","high","low","close","volume"]:
        df[col] = df[col].astype(float)
    df = df[["open_time","open","high","low","close","volume"]].copy()
    df.set_index("open_time", inplace=True)
    df.sort_index(inplace=True)
    return df
