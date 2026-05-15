import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, "src")
from data_fetcher      import fetch_binance
from feature_generator import engineer_features
from labeler           import generate_labels
from sentiment         import fetch_fear_greed, merge_fear_greed

st.set_page_config(
    page_title="CryptoSense DSS",
    page_icon="₿",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=DM+Sans:wght@400;500;600&display=swap');

html, body, .stApp {
    background-color: #0b0c10;
    font-family: 'IBM Plex Mono', monospace;
    color: #c9d1d9;
}
#MainMenu, footer, header { visibility: hidden; }

h1, h2, h3 {
    font-family: 'DM Sans', sans-serif !important;
    color: #e6edf3 !important;
    font-weight: 600 !important;
}
h1 { font-size: 1.6rem !important; letter-spacing: 0.3px; }
h2 { font-size: 1.1rem !important; border-left: 3px solid #f0b429;
     padding-left: 10px; margin-top: 2rem !important; }
h3 { font-size: 0.85rem !important; color: #4b5563 !important;
     text-transform: uppercase; letter-spacing: 2px; }

[data-testid="metric-container"] {
    background: #0d0e14;
    border: 1px solid #1e2030;
    border-radius: 8px;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #4b5563 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 600 !important;
    color: #e6edf3 !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
}

[data-testid="stSidebar"] {
    background: #0d0e14;
    border-right: 1px solid #1e2030;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: #6b7280;
    font-size: 0.75rem;
}

.stButton > button {
    background: #f0b429 !important;
    color: #0b0c10 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 12px !important;
}
.stButton > button:hover {
    background: #e6a820 !important;
}

.stSelectbox > div > div, .stSlider {
    background: #0d0e14 !important;
}

.stDataFrame {
    border: 1px solid #1e2030 !important;
    border-radius: 8px !important;
}

.stAlert {
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
}

.signal-card {
    border-radius: 8px;
    padding: 24px;
    text-align: center;
}
.signal-buy  { background:#0d2018; border:1px solid #1e4d2b; }
.signal-sell { background:#1a0d0d; border:1px solid #4d1e1e; }
.signal-hold { background:#141208; border:1px solid #3d3010; }

.rule { border:none; border-top:1px solid #1e2030; margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<p style='font-family:DM Sans; font-size:1.1rem; "
        "font-weight:600; color:#e6edf3; margin-bottom:4px'>"
        "CryptoSense DSS</p>"
        "<p style='font-size:0.7rem; color:#f0b429; "
        "letter-spacing:2px; margin-top:0'>DECISION SUPPORT SYSTEM</p>",
        unsafe_allow_html=True
    )
    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    symbol   = st.selectbox("Asset", ["BTCUSDT","ETHUSDT","BNBUSDT"])
    interval = st.selectbox("Timeframe", ["1d","4h","1h"])
    limit    = st.slider("Candles", 200, 1000, 500, 100)
    threshold = st.slider("Signal threshold (%)", 1, 5, 2, 1)

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)
    run = st.button("Run Analysis", use_container_width=True)
    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.7rem; color:#4b5563; line-height:1.8'>"
        "Model: XGBoost (tuned)<br>"
        "Balancing: SMOTE<br>"
        "Features: 19 indicators<br>"
        "Sentiment: Fear & Greed Index<br>"
        "Data: Binance API</p>",
        unsafe_allow_html=True
    )

# ── Welcome ──────────────────────────────────────────────────────────
if not run:
    st.markdown("## CryptoSense &mdash; Decision Support System")
    st.markdown(
        "<p style='color:#6b7280; font-size:0.85rem; "
        "font-family:IBM Plex Mono'>Configure settings on the left "
        "and run the analysis to generate live ML signals.</p>",
        unsafe_allow_html=True
    )
    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("## Pipeline")
        st.markdown("""
<p style='font-size:0.82rem; color:#6b7280; line-height:2; font-family:IBM Plex Mono'>
1. Fetch OHLCV data from Binance API<br>
2. Compute 19 technical indicators<br>
3. Fetch Fear & Greed sentiment index<br>
4. Generate Buy / Hold / Sell labels<br>
5. Predict with tuned XGBoost model<br>
6. Backtest against Buy & Hold strategy
</p>
""", unsafe_allow_html=True)

    with c2:
        st.markdown("## Signal Logic")
        st.markdown("""
<p style='font-size:0.82rem; color:#6b7280; line-height:2; font-family:IBM Plex Mono'>
Next-day return above +2%  &rarr;  BUY<br>
Next-day return below  -2%  &rarr;  SELL<br>
Everything in between     &rarr;  HOLD<br><br>
Threshold adjustable in sidebar.<br>
Labels generated on historical data;<br>
model learns patterns from them.
</p>
""", unsafe_allow_html=True)

# ── Analysis ─────────────────────────────────────────────────────────
if run:
    bar = st.progress(0, text="Fetching data from Binance...")

    try:
        df = fetch_binance(symbol, interval, limit)
    except Exception as e:
        st.error(f"Data fetch failed: {e}")
        st.stop()

    bar.progress(25, text="Engineering technical indicators...")
    df = engineer_features(df)

    bar.progress(45, text="Fetching Fear & Greed Index...")
    try:
        fg = fetch_fear_greed(limit)
        df = merge_fear_greed(df, fg)
    except:
        df["fear_greed_value"] = 50

    bar.progress(60, text="Generating labels...")
    df = generate_labels(df,
            buy_threshold=threshold/100,
            sell_threshold=-threshold/100)

    bar.progress(80, text="Running model predictions...")
    try:
        model      = joblib.load("models/buy_sell_classifier.pkl")
        scaler     = joblib.load("models/scaler.pkl")
        feat_cols  = joblib.load("models/feature_cols.pkl")
        cols       = [c for c in feat_cols if c in df.columns]
        clean      = df[cols].dropna()
        X          = scaler.transform(clean.values)
        preds      = model.predict(X)
        df_pred    = pd.DataFrame({
            "prediction": preds,
            "signal": [["SELL","HOLD","BUY"][p] for p in preds]
        }, index=clean.index)
        if "signal" in df.columns:
            df = df.drop(columns=["signal"])
        if "prediction" in df.columns:
            df = df.drop(columns=["prediction"])
        df = df.join(df_pred, how="left")
    except Exception as e:
        st.error(f"Prediction failed: {e}")
        st.stop()

    bar.progress(100, text="Complete.")
    bar.empty()

    # ── Signal ────────────────────────────────────────────
    latest       = df["signal"].dropna().iloc[-1]
    latest_price = df["close"].iloc[-1]
    latest_fg    = int(df["fear_greed_value"].iloc[-1])
    latest_rsi   = df["rsi"].iloc[-1]
    latest_macd  = df["macd_diff"].iloc[-1]

    sig_color = {"BUY":"#3fb950","SELL":"#f85149","HOLD":"#e6b430"}[latest]
    sig_class = {"BUY":"signal-buy","SELL":"signal-sell","HOLD":"signal-hold"}[latest]

    st.markdown("## Current Signal")
    col_sig, col_m = st.columns([1,3])

    with col_sig:
        st.markdown(f"""
        <div class="signal-card {sig_class}">
            <p style="font-size:0.7rem; color:{sig_color};
               letter-spacing:3px; font-family:IBM Plex Mono;
               margin-bottom:8px">RECOMMENDATION</p>
            <p style="font-size:2.5rem; font-weight:600;
               color:{sig_color}; font-family:DM Sans;
               margin:0; letter-spacing:2px">{latest}</p>
            <p style="font-size:0.7rem; color:#4b5563;
               font-family:IBM Plex Mono; margin-top:8px">
               {symbol} &mdash; {interval}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_m:
        m1,m2,m3,m4 = st.columns(4)
        with m1:
            st.metric("Price", f"${latest_price:,.0f}")
        with m2:
            rsi_note = ("Overbought" if latest_rsi > 70
                       else "Oversold" if latest_rsi < 30
                       else "Neutral")
            st.metric("RSI (14)", f"{latest_rsi:.1f}", rsi_note)
        with m3:
            fg_note = ("Extreme Fear" if latest_fg < 25
                      else "Fear" if latest_fg < 50
                      else "Greed" if latest_fg < 75
                      else "Extreme Greed")
            st.metric("Fear & Greed", f"{latest_fg}/100", fg_note)
        with m4:
            st.metric("MACD Signal",
                      f"{latest_macd:.0f}",
                      "Bullish" if latest_macd > 0 else "Bearish")

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    # ── Price Chart ───────────────────────────────────────
    st.markdown("## Price Chart")

    fig, ax = plt.subplots(figsize=(13,4), facecolor="#0b0c10")
    ax.set_facecolor("#0d0e14")
    for sp in ax.spines.values(): sp.set_edgecolor("#1e2030")
    ax.tick_params(colors="#4b5563", labelsize=8)
    ax.yaxis.tick_right()

    x = range(len(df))
    ax.plot(x, df["close"], color="#378add",
            linewidth=1.5, zorder=2)
    ax.fill_between(x, df["close"], df["close"].min(),
                    alpha=0.06, color="#378add")

    buys  = df[df["signal"]=="BUY"]
    sells = df[df["signal"]=="SELL"]
    idx_list = list(df.index)
    bx = [idx_list.index(i) for i in buys.index  if i in idx_list]
    sx = [idx_list.index(i) for i in sells.index if i in idx_list]

    ax.scatter(bx,  buys["close"].values,  marker="^",
               color="#3fb950", s=70, zorder=5)
    ax.scatter(sx, sells["close"].values,  marker="v",
               color="#f85149", s=70, zorder=5)

    ax.set_ylabel("USDT", color="#4b5563",
                  fontsize=8, fontfamily="monospace")
    ax.grid(axis="y", color="#1e2030",
            linewidth=0.5, linestyle="--")

    from matplotlib.lines import Line2D
    legend = ax.legend(handles=[
        Line2D([0],[0], marker="^", color="#3fb950",
               linestyle="None", markersize=7, label="Buy signal"),
        Line2D([0],[0], marker="v", color="#f85149",
               linestyle="None", markersize=7, label="Sell signal"),
        Line2D([0],[0], color="#378add",
               linewidth=1.5, label="Price"),
    ], facecolor="#0d0e14", edgecolor="#1e2030",
       labelcolor="#6b7280", fontsize=8, framealpha=1)

    st.pyplot(fig)
    plt.close()

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    # ── Backtest ──────────────────────────────────────────
    st.markdown("## Backtest Simulation")
    st.markdown(
        "<p style='font-size:0.78rem; color:#4b5563; "
        "font-family:IBM Plex Mono'>Starting capital: $10,000 "
        "&mdash; Buy on BUY signal, sell on SELL signal, "
        "hold otherwise.</p>",
        unsafe_allow_html=True
    )

    initial   = 10_000.0
    cash      = initial
    holdings  = 0.0
    portfolio = []
    trades    = 0
    df_bt     = df.dropna(subset=["signal"]).copy()

    for _, row in df_bt.iterrows():
        price = row["close"]
        sig   = row["signal"]
        if sig == "BUY" and holdings == 0:
            holdings = cash / price; cash = 0.0; trades += 1
        elif sig == "SELL" and holdings > 0:
            cash = holdings * price; holdings = 0.0; trades += 1
        portfolio.append(cash + holdings * price)

    df_bt["strategy"] = portfolio
    df_bt["bah"]      = (initial / df_bt["close"].iloc[0]) \
                         * df_bt["close"]

    final_s = df_bt["strategy"].iloc[-1]
    final_b = df_bt["bah"].iloc[-1]
    ret_s   = (final_s - initial) / initial * 100
    ret_b   = (final_b - initial) / initial * 100

    b1,b2,b3,b4 = st.columns(4)
    with b1: st.metric("ML Strategy",  f"${final_s:,.0f}", f"{ret_s:+.2f}%")
    with b2: st.metric("Buy & Hold",   f"${final_b:,.0f}", f"{ret_b:+.2f}%")
    with b3: st.metric("Outperformance", f"{ret_s-ret_b:+.2f}%", "vs passive")
    with b4: st.metric("Trades made",  trades)

    fig2, ax2 = plt.subplots(figsize=(13,3.5), facecolor="#0b0c10")
    ax2.set_facecolor("#0d0e14")
    for sp in ax2.spines.values(): sp.set_edgecolor("#1e2030")
    ax2.tick_params(colors="#4b5563", labelsize=8)
    ax2.yaxis.tick_right()

    x2 = range(len(df_bt))
    ax2.plot(x2, df_bt["strategy"], color="#a855f7",
             linewidth=2, label=f"ML strategy")
    ax2.plot(x2, df_bt["bah"], color="#f0b429",
             linewidth=1.5, linestyle="--", label="Buy & Hold")
    ax2.axhline(initial, color="#1e2030",
                linewidth=0.8, linestyle=":")
    ax2.fill_between(x2, df_bt["strategy"], initial,
        where=[v >= initial for v in df_bt["strategy"]],
        alpha=0.1, color="#a855f7")
    ax2.fill_between(x2, df_bt["strategy"], initial,
        where=[v < initial for v in df_bt["strategy"]],
        alpha=0.1, color="#f85149")
    ax2.grid(axis="y", color="#1e2030",
             linewidth=0.5, linestyle="--")
    ax2.legend(facecolor="#0d0e14", edgecolor="#1e2030",
               labelcolor="#6b7280", fontsize=8)

    st.pyplot(fig2)
    plt.close()

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    # ── Recent Predictions Table ──────────────────────────
    st.markdown("## Recent Predictions")

    display = df[["close","rsi","macd",
                  "fear_greed_value","signal"]
                ].dropna().tail(20).copy()
    display.columns = ["Close price","RSI",
                       "MACD","Fear & Greed","Signal"]
    display["Close price"] = display["Close price"].apply(
                              lambda x: f"${x:,.2f}")
    display["RSI"]  = display["RSI"].apply(
                       lambda x: f"{x:.1f}")
    display["MACD"] = display["MACD"].apply(
                       lambda x: f"{x:,.0f}")

    st.dataframe(display, use_container_width=True)