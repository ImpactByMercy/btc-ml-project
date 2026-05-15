import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib
import os
import warnings
warnings.filterwarnings("ignore")

LABEL_MAP       = {0: "SELL", 1: "HOLD", 2: "BUY"}
INITIAL_CAPITAL = 10_000.0
FEATURE_COLS = [
    "return_1d", "return_7d", "volatility_7d", "volatility_14d",
    "rsi", "macd", "macd_signal", "macd_diff",
    "bb_width", "bb_pct", "stoch_k", "stoch_d",
    "atr", "sma_20", "sma_50",
    "price_vs_sma20", "price_vs_sma50",
    "volume_ratio", "fear_greed_value"
]


def load_model():
    model      = joblib.load("models/buy_sell_classifier.pkl")
    scaler     = joblib.load("models/scaler.pkl")
    return model, scaler


def time_split(df):
    n  = len(df)
    t2 = int(n * 0.85)
    return df.iloc[t2:]


def prepare_test(df):
    cols    = [c for c in FEATURE_COLS if c in df.columns]
    clean   = df[cols + ["label", "close"]].dropna()
    X       = clean[cols].values
    y       = clean["label"].values
    return X, y, clean


def backtest(test_df, predictions):
    df        = test_df.copy()
    df        = df.iloc[:len(predictions)]
    df["prediction"] = predictions

    cash      = INITIAL_CAPITAL
    holdings  = 0.0
    portfolio = []
    trades    = 0

    for _, row in df.iterrows():
        price  = row["close"]
        signal = row["prediction"]

        if signal == 2 and holdings == 0:   # BUY
            holdings = cash / price
            cash     = 0.0
            trades  += 1
        elif signal == 0 and holdings > 0:  # SELL
            cash     = holdings * price
            holdings = 0.0
            trades  += 1

        total = cash + holdings * price
        portfolio.append(total)

    df["strategy_value"] = portfolio

    # Buy and Hold baseline
    entry              = df["close"].iloc[0]
    df["bah_value"]    = (INITIAL_CAPITAL / entry) * df["close"]

    # Random baseline
    np.random.seed(42)
    rand_preds         = np.random.choice([0,1,2], size=len(df))
    rand_cash          = INITIAL_CAPITAL
    rand_hold          = 0.0
    rand_portfolio     = []
    for i, row in df.iterrows():
        price = row["close"]
        sig   = rand_preds[len(rand_portfolio)]
        if sig == 2 and rand_hold == 0:
            rand_hold = rand_cash / price
            rand_cash = 0.0
        elif sig == 0 and rand_hold > 0:
            rand_cash = rand_hold * price
            rand_hold = 0.0
        rand_portfolio.append(rand_cash + rand_hold * price)
    df["random_value"] = rand_portfolio

    # Results
    final_strat  = df["strategy_value"].iloc[-1]
    final_bah    = df["bah_value"].iloc[-1]
    final_rand   = df["random_value"].iloc[-1]

    strat_return = (final_strat - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    bah_return   = (final_bah   - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    rand_return  = (final_rand  - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

    print("\n" + "═"*50)
    print("  BACKTEST RESULTS")
    print("═"*50)
    print(f"  Initial Capital   : ${INITIAL_CAPITAL:,.2f}")
    print(f"  ML Strategy Final : ${final_strat:,.2f}  ({strat_return:+.2f}%)")
    print(f"  Buy & Hold Final  : ${final_bah:,.2f}  ({bah_return:+.2f}%)")
    print(f"  Random Strategy   : ${final_rand:,.2f}  ({rand_return:+.2f}%)")
    print(f"  Total Trades Made : {trades}")
    print("═"*50)

    return df, strat_return, bah_return, rand_return


def plot_results(df, strat_return, bah_return, rand_return):
    os.makedirs("data/processed", exist_ok=True)
    fig, axes = plt.subplots(3, 1, figsize=(14, 12),
                             facecolor="#0e1117")

    for ax in axes:
        ax.set_facecolor("#161b22")
        for sp in ax.spines.values():
            sp.set_edgecolor("#30363d")
        ax.tick_params(colors="#8b949e")
        ax.yaxis.label.set_color("#8b949e")
        ax.title.set_color("#e6edf3")

    # ── 1. Price + signals ───────────────────────────────
    ax = axes[0]
    ax.plot(range(len(df)), df["close"],
            color="#58a6ff", linewidth=1.5, label="BTC Price")
    buys  = df[df["prediction"] == 2]
    sells = df[df["prediction"] == 0]
    buy_idx  = [df.index.get_loc(i) for i in buys.index
                if i in df.index]
    sell_idx = [df.index.get_loc(i) for i in sells.index
                if i in df.index]
    ax.scatter(buy_idx,  buys["close"],
               marker="^", color="#3fb950", s=80,
               zorder=5, label="BUY signal")
    ax.scatter(sell_idx, sells["close"],
               marker="v", color="#f85149", s=80,
               zorder=5, label="SELL signal")
    ax.set_title("BTC Price with Model Signals", fontsize=13,
                 fontweight="bold")
    ax.set_ylabel("Price (USDT)")
    ax.legend(facecolor="#161b22", edgecolor="#30363d",
              labelcolor="#e6edf3")

    # ── 2. Portfolio comparison ──────────────────────────
    ax = axes[1]
    ax.plot(range(len(df)), df["strategy_value"],
            color="#d2a8ff", linewidth=2,
            label=f"ML Strategy ({strat_return:+.1f}%)")
    ax.plot(range(len(df)), df["bah_value"],
            color="#ffa657", linewidth=2, linestyle="--",
            label=f"Buy & Hold ({bah_return:+.1f}%)")
    ax.plot(range(len(df)), df["random_value"],
            color="#8b949e", linewidth=1.5, linestyle=":",
            label=f"Random ({rand_return:+.1f}%)")
    ax.axhline(INITIAL_CAPITAL, color="#8b949e",
               linewidth=0.8, linestyle=":")
    ax.set_title("Portfolio Value Comparison", fontsize=13,
                 fontweight="bold")
    ax.set_ylabel("Portfolio ($)")
    ax.legend(facecolor="#161b22", edgecolor="#30363d",
              labelcolor="#e6edf3")

    # ── 3. Signal distribution ───────────────────────────
    ax = axes[2]
    counts = df["prediction"].value_counts().sort_index()
    labels = [LABEL_MAP.get(i, str(i)) for i in counts.index]
    colors = ["#f85149", "#8b949e", "#3fb950"][:len(counts)]
    bars   = ax.bar(labels, counts.values, color=colors,
                    edgecolor="#30363d")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5, str(val),
                ha="center", color="#e6edf3", fontsize=11)
    ax.set_title("Signal Distribution on Test Set",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("Count")

    plt.tight_layout(pad=2.5)
    path = "data/processed/backtest_results.png"
    plt.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"[✓] Chart saved → {path}")
    return path


if __name__ == "__main__":
    df = pd.read_csv(
        "data/processed/BTCUSDT_labeled.csv",
        index_col="open_time"
    )

    model, scaler = load_model()
    test_df       = time_split(df)
    X_test, y_test, clean_test = prepare_test(test_df)
    X_scaled      = scaler.transform(X_test)
    predictions   = model.predict(X_scaled)

    result_df, strat_return, bah_return, rand_return = backtest(
        clean_test, predictions)

    plot_results(result_df, strat_return, bah_return, rand_return)