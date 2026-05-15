import pandas as pd
import numpy as np
import ta
import os

def engineer_features(df):
    df = df.copy()
    close = df["close"]
    high  = df["high"]
    low   = df["low"]

    # ── Returns ──────────────────────────────────────
    df["return_1d"]     = close.pct_change(1)
    df["return_7d"]     = close.pct_change(7)
    df["volatility_7d"] = df["return_1d"].rolling(7).std()
    df["volatility_14d"]= df["return_1d"].rolling(14).std()

    # ── Moving Averages ──────────────────────────────
    df["sma_20"]  = close.rolling(20).mean()
    df["sma_50"]  = close.rolling(50).mean()
    df["sma_200"] = close.rolling(200).mean()
    df["ema_12"]  = close.ewm(span=12, adjust=False).mean()
    df["ema_26"]  = close.ewm(span=26, adjust=False).mean()

    # ── RSI ──────────────────────────────────────────
    df["rsi"] = ta.momentum.RSIIndicator(close, window=14).rsi()

    # ── MACD ─────────────────────────────────────────
    macd = ta.trend.MACD(close)
    df["macd"]        = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"]   = macd.macd_diff()

    # ── Bollinger Bands ───────────────────────────────
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    df["bb_upper"]  = bb.bollinger_hband()
    df["bb_lower"]  = bb.bollinger_lband()
    df["bb_middle"] = bb.bollinger_mavg()
    df["bb_width"]  = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
    df["bb_pct"]    = bb.bollinger_pband()

    # ── Stochastic Oscillator ─────────────────────────
    stoch = ta.momentum.StochasticOscillator(
                high, low, close, window=14, smooth_window=3)
    df["stoch_k"] = stoch.stoch()
    df["stoch_d"] = stoch.stoch_signal()

    # ── ATR (volatility) ──────────────────────────────
    df["atr"] = ta.volatility.AverageTrueRange(
                    high, low, close, window=14).average_true_range()

    # ── Volume ────────────────────────────────────────
    df["volume_sma_20"] = df["volume"].rolling(20).mean()
    df["volume_ratio"]  = df["volume"] / df["volume_sma_20"]

    # ── Price vs Moving Averages ──────────────────────
    df["price_vs_sma20"]  = (close - df["sma_20"])  / df["sma_20"]
    df["price_vs_sma50"]  = (close - df["sma_50"])  / df["sma_50"]
    df["price_vs_sma200"] = (close - df["sma_200"]) / df["sma_200"]

    return df

def save_processed(df, symbol="BTCUSDT"):
    os.makedirs("data/processed", exist_ok=True)
    path = f"data/processed/{symbol}_features.csv"
    df.to_csv(path)
    print(f"Saved {len(df)} rows, {len(df.columns)} columns to {path}")

if __name__ == "__main__":
    df = pd.read_csv("data/raw/BTCUSDT_raw.csv", index_col="open_time")
    print("Running feature engineering...")
    df = engineer_features(df)
    save_processed(df)
    print(df[["close","rsi","macd","bb_width","stoch_k"]].tail(5))