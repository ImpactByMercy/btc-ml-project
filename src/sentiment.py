import requests
import pandas as pd

def fetch_fear_greed(limit=500):
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json().get("data", [])
    df = pd.DataFrame(data)
    df["date"]             = pd.to_datetime(df["timestamp"].astype(int), unit="s").dt.normalize()
    df["fear_greed_value"] = df["value"].astype(int)
    df["fear_greed_label"] = df["value_classification"]
    df = df[["date","fear_greed_value","fear_greed_label"]].copy()
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)
    return df

def merge_fear_greed(price_df, fg_df):
    price_df = price_df.copy()
    price_df["_date"] = price_df.index.normalize()
    fg_reset = fg_df.reset_index().rename(columns={"date": "_date"})
    merged = price_df.reset_index().merge(fg_reset, on="_date", how="left")
    merged = merged.set_index(price_df.index.name or "open_time")
    merged.drop(columns=["_date"], inplace=True)
    merged["fear_greed_value"] = merged["fear_greed_value"].ffill().fillna(50)
    merged["fear_greed_label"] = merged["fear_greed_label"].ffill().fillna("Neutral")
    return merged
