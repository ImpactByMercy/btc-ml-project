import requests
import pandas as pd

def fetch_fear_greed(limit=1000):
    """
    Fetch historical Fear & Greed Index from alternative.me API.
    Returns a DataFrame with date and fear_greed_value columns.
    """
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()["data"]
        
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(
                            df["timestamp"].astype(int), unit="s")
        df["timestamp"] = df["timestamp"].dt.normalize()
        df = df.rename(columns={
            "value":              "fear_greed_value",
            "value_classification":"fear_greed_label",
            "timestamp":          "date"
        })
        df["fear_greed_value"] = df["fear_greed_value"].astype(int)
        df = df[["date","fear_greed_value","fear_greed_label"]]
        df = df.sort_values("date").reset_index(drop=True)
        
        print(f"Fetched {len(df)} days of Fear & Greed data")
        return df
    
    except Exception as e:
        print(f"Could not fetch Fear & Greed Index: {e}")
        return None

def merge_fear_greed(price_df, fg_df):
    """
    Merge Fear & Greed data into the main price DataFrame.
    """
    price_df = price_df.copy()
    price_df.index = pd.to_datetime(price_df.index).normalize()
    
    fg_df = fg_df.set_index("date")
    
    price_df = price_df.join(
                fg_df[["fear_greed_value","fear_greed_label"]],
                how="left")
    
    # Fill any missing values with neutral (50)
    price_df["fear_greed_value"] = price_df[
                                    "fear_greed_value"].fillna(50)
    price_df["fear_greed_label"] = price_df[
                                    "fear_greed_label"].fillna("Neutral")
    
    filled = price_df["fear_greed_value"].isna().sum()
    print(f"Merged Fear & Greed — {filled} missing values filled")
    return price_df

if __name__ == "__main__":
    fg = fetch_fear_greed(limit=1000)
    print(fg.tail(5))
    print(f"\nLatest value: {fg['fear_greed_value'].iloc[-1]} "
          f"({fg['fear_greed_label'].iloc[-1]})")