#!/usr/bin/env python
"""
Train a real XGBoost model on Binance BTCUSDT historical data.
Saves buy_sell_classifier.pkl, scaler.pkl, feature_cols.pkl to backend/models/
"""

import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data_fetcher import fetch_binance
from src.feature_generator import engineer_features
from src.sentiment import fetch_fear_greed, merge_fear_greed
from src.labeler import generate_labels

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

print("=" * 50)
print("CryptoSense DSS — Model Training")
print("=" * 50)

# --- 1. Fetch data (3 assets x 1000 days for a richer dataset) ---
print("\n[1/6] Fetching Binance data...")
dfs = []
for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
    print(f"  Fetching {symbol}...")
    df = fetch_binance(symbol, "1d", 1000)
    df["symbol"] = symbol
    dfs.append(df)
df_all = pd.concat(dfs)
print(f"  Total rows: {len(df_all)}")

# --- 2. Engineer features ---
print("\n[2/6] Engineering features...")
results = []
for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
    subset = df_all[df_all["symbol"] == symbol].drop(columns=["symbol"])
    subset = engineer_features(subset)
    results.append(subset)
df_feat = pd.concat(results)

# --- 3. Merge Fear & Greed ---
print("\n[3/6] Fetching Fear & Greed index...")
try:
    fg = fetch_fear_greed(1000)
    df_feat = merge_fear_greed(df_feat, fg)
    print("  Fear & Greed merged successfully.")
except Exception as e:
    print(f"  Warning: {e} — using neutral value 50")
    df_feat["fear_greed_value"] = 50

# --- 4. Generate labels ---
print("\n[4/6] Generating labels...")
df_feat = generate_labels(df_feat, buy_threshold=0.02, sell_threshold=-0.02)

feature_cols = [
    'open', 'high', 'low', 'close', 'volume',
    'rsi', 'macd', 'macd_signal', 'macd_diff',
    'bb_upper', 'bb_lower', 'bb_middle',
    'fear_greed_value',
    'sma_20', 'sma_50', 'sma_200',
    'ema_12', 'ema_26',
    'momentum', 'price_change'
]

cols = [c for c in feature_cols if c in df_feat.columns]
df_clean = df_feat[cols + ['label']].dropna()
print(f"  Clean rows for training: {len(df_clean)}")

X = df_clean[cols].values
y = df_clean['label'].astype(int).values

print(f"  Label distribution: {dict(zip(*np.unique(y, return_counts=True)))}")

# --- 5. Train/test split + SMOTE ---
print("\n[5/6] Training XGBoost with SMOTE balancing...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

try:
    sm = SMOTE(random_state=42)
    X_train, y_train = sm.fit_resample(X_train, y_train)
    print(f"  After SMOTE: {len(X_train)} training samples")
except Exception as e:
    print(f"  SMOTE skipped: {e}")

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42
)
model.fit(X_train, y_train)

# --- 6. Evaluate & save ---
print("\n[6/6] Evaluating and saving model...")
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["SELL", "HOLD", "BUY"]))

models_dir = Path(__file__).parent / 'backend' / 'models'
models_dir.mkdir(exist_ok=True)

joblib.dump(model,        models_dir / 'buy_sell_classifier.pkl')
joblib.dump(scaler,       models_dir / 'scaler.pkl')
joblib.dump(cols,         models_dir / 'feature_cols.pkl')

print(f"\n✓ Models saved to {models_dir}")
print("  - buy_sell_classifier.pkl  (XGBoost)")
print("  - scaler.pkl               (StandardScaler)")
print("  - feature_cols.pkl         (20 features)")
print("\nTraining complete! Restart the backend to use the new model.")
