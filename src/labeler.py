import pandas as pd
import os

def generate_labels(df, buy_threshold=0.02, sell_threshold=-0.02):
    df = df.copy()

    # Calculate next day's return
    df["future_return"] = df["close"].pct_change().shift(-1)

    def label(row):
        if pd.isna(row["future_return"]):
            return None
        if row["future_return"] > buy_threshold:
            return 2   # BUY
        elif row["future_return"] < sell_threshold:
            return 0   # SELL
        else:
            return 1   # HOLD

    df["label"]  = df.apply(label, axis=1)
    df["signal"] = df["label"].map({0:"SELL", 1:"HOLD", 2:"BUY"})

    # Drop last row (no future return available)
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    # Print distribution
    total  = len(df)
    counts = df["signal"].value_counts()
    print("Label Distribution:")
    for sig in ["BUY", "HOLD", "SELL"]:
        n = counts.get(sig, 0)
        print(f"  {sig}:  {n} rows  ({100*n/total:.1f}%)")

    return df

def save_labeled(df, symbol="BTCUSDT"):
    os.makedirs("data/processed", exist_ok=True)
    path = f"data/processed/{symbol}_labeled.csv"
    df.to_csv(path)
    print(f"Saved labeled data to {path}")

if __name__ == "__main__":
    df = pd.read_csv(
        "data/processed/BTCUSDT_features.csv",
        index_col="open_time"
    )
    print("Generating labels...")
    df = generate_labels(df)
    save_labeled(df)
    print(df[["close","future_return","signal"]].tail(5))