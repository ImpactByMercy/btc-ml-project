import pandas as pd
import numpy as np

def engineer_features(df):
    df = df.copy()

    # SMAs
    df["sma_20"]  = df["close"].rolling(20).mean()
    df["sma_50"]  = df["close"].rolling(50).mean()
    df["sma_200"] = df["close"].rolling(200).mean()

    # EMAs
    df["ema_12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_26"] = df["close"].ewm(span=26, adjust=False).mean()

    # MACD
    df["macd"]        = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_diff"]   = df["macd"] - df["macd_signal"]

    # RSI (14)
    delta = df["close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    # Bollinger Bands (20, 2sigma)
    df["bb_middle"] = df["close"].rolling(20).mean()
    bb_std          = df["close"].rolling(20).std()
    df["bb_upper"]  = df["bb_middle"] + 2 * bb_std
    df["bb_lower"]  = df["bb_middle"] - 2 * bb_std

    # Momentum (10-period)
    df["momentum"] = df["close"] - df["close"].shift(10)

    # Price change (1-period return)
    df["price_change"] = df["close"].pct_change()

    return df
