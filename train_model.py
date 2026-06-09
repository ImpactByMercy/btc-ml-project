import sys, joblib, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf
from src.feature_generator import engineer_features
from src.labeler import generate_labels
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
print("Fetching Yahoo Finance data...")
symbols = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "BNB-USD": "BNBUSDT"}
dfs = []
for yf_sym, label in symbols.items():
    print(f"  {yf_sym}...")
    df = yf.Ticker(yf_sym).history(period="3y", interval="1d")
    df = df.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
    df = df[["open","high","low","close","volume"]].copy()
    df.index = df.index.tz_localize(None)
    df.index.name = "open_time"
    df["symbol"] = label
    dfs.append(df)
df_all = pd.concat(dfs)
print(f"Total rows: {len(df_all)}")
results = []
for sym in ["BTCUSDT","ETHUSDT","BNBUSDT"]:
    subset = df_all[df_all["symbol"]==sym].drop(columns=["symbol"])
    results.append(engineer_features(subset))
df_feat = pd.concat(results)
try:
    from src.sentiment import fetch_fear_greed, merge_fear_greed
    df_feat = merge_fear_greed(df_feat, fetch_fear_greed(1000))
    print("Fear and Greed merged.")
except Exception as e:
    print(f"Fallback: {e}")
    df_feat["fear_greed_value"] = 50
df_feat = generate_labels(df_feat, buy_threshold=0.02, sell_threshold=-0.02)
feature_cols = ["open","high","low","close","volume","rsi","macd","macd_signal","macd_diff","bb_upper","bb_lower","bb_middle","fear_greed_value","sma_20","sma_50","sma_200","ema_12","ema_26","momentum","price_change"]
cols = [c for c in feature_cols if c in df_feat.columns]
df_clean = df_feat[cols + ["label"]].dropna()
X = df_clean[cols].values
y = df_clean["label"].astype(int).values
print(f"Clean rows: {len(df_clean)}")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
try:
    X_train, y_train = SMOTE(random_state=42).fit_resample(X_train, y_train)
    print(f"After SMOTE: {len(X_train)}")
except Exception as e:
    print(f"SMOTE skipped: {e}")
model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, eval_metric="mlogloss", random_state=42)
model.fit(X_train, y_train)
print(classification_report(model.predict(X_test), y_test, target_names=["SELL","HOLD","BUY"]))
models_dir = Path(__file__).parent / "backend" / "models"
models_dir.mkdir(exist_ok=True)
joblib.dump(model, models_dir / "buy_sell_classifier.pkl")
joblib.dump(scaler, models_dir / "scaler.pkl")
joblib.dump(cols, models_dir / "feature_cols.pkl")
print("Models saved. Training complete.")