import pandas as pd
import numpy as np

def generate_labels(df, buy_threshold=0.02, sell_threshold=-0.02, forward_periods=1):
    df = df.copy()
    df["future_return"] = (df["close"].shift(-forward_periods) - df["close"]) / df["close"]
    conditions = [df["future_return"] >= buy_threshold, df["future_return"] <= sell_threshold]
    df["label"] = np.select(conditions, [2, 0], default=1)
    df.loc[df["future_return"].isna(), "label"] = np.nan
    return df
