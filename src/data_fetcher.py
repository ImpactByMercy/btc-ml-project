import requests
import pandas as pd
import os

def fetch_binance(symbol="BTCUSDT", interval="1d", limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_base_volume", "taker_quote_volume", "ignore"
    ])

    df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.drop(columns=["ignore"])
    df = df.set_index("open_time")
    return df

def save_raw(df, symbol="BTCUSDT"):
    os.makedirs("data/raw", exist_ok=True)
    path = f"data/raw/{symbol}_raw.csv"
    df.to_csv(path)
    print(f"Saved {len(df)} rows to {path}")

if __name__ == "__main__":
    print("Fetching Bitcoin data from Binance...")
    df = fetch_binance("BTCUSDT", "1d", 1000)
    save_raw(df)
    print(df.tail(3))