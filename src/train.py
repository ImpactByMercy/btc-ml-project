import pandas as pd
import numpy as np
import joblib
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, f1_score,
                             classification_report)
from sklearn.model_selection import RandomizedSearchCV
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import lightgbm as lgb

FEATURE_COLS = [
    "return_1d", "return_7d", "volatility_7d", "volatility_14d",
    "rsi", "macd", "macd_signal", "macd_diff",
    "bb_width", "bb_pct", "stoch_k", "stoch_d",
    "atr", "sma_20", "sma_50",
    "price_vs_sma20", "price_vs_sma50",
    "volume_ratio",
    "fear_greed_value"        # ← sentiment feature
]

LABEL_NAMES = ["SELL", "HOLD", "BUY"]


def time_split(df):
    n  = len(df)
    t1 = int(n * 0.70)
    t2 = int(n * 0.85)
    train = df.iloc[:t1]
    val   = df.iloc[t1:t2]
    test  = df.iloc[t2:]
    print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    return train, val, test


def prepare_xy(df):
    cols = [c for c in FEATURE_COLS if c in df.columns]
    sub  = df[cols + ["label"]].dropna()
    X    = sub[cols].values
    y    = sub["label"].values
    return X, y


def apply_smote(X, y):
    print("\nApplying SMOTE to fix class imbalance...")
    before = pd.Series(y).value_counts().to_dict()
    sm     = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X, y)
    after  = pd.Series(y_res).value_counts().to_dict()
    label_map = {0:"SELL", 1:"HOLD", 2:"BUY"}
    print("Before SMOTE:")
    for k,v in sorted(before.items()):
        print(f"  {label_map[k]}: {v}")
    print("After SMOTE:")
    for k,v in sorted(after.items()):
        print(f"  {label_map[k]}: {v}")
    return X_res, y_res


def tune_and_train(df):
    os.makedirs("models", exist_ok=True)

    train_df, val_df, test_df = time_split(df)

    X_train, y_train = prepare_xy(train_df)
    X_test,  y_test  = prepare_xy(test_df)

    # Scale
    scaler     = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # Apply SMOTE on training data only
    X_train_bal, y_train_bal = apply_smote(X_train_sc, y_train)

    # ── Hyperparameter Grids ──────────────────────────────────────
    param_grids = {
        "Random Forest": {
            "model": RandomForestClassifier(
                        class_weight="balanced", random_state=42),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth":    [5, 8, 10, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf":  [1, 2, 4]
            }
        },
        "XGBoost": {
            "model": xgb.XGBClassifier(
                        eval_metric="mlogloss",
                        random_state=42, verbosity=0),
            "params": {
                "n_estimators":  [100, 200, 300],
                "learning_rate": [0.01, 0.05, 0.1],
                "max_depth":     [3, 5, 7],
                "subsample":     [0.7, 0.8, 1.0]
            }
        },
        "LightGBM": {
            "model": lgb.LGBMClassifier(
                        class_weight="balanced",
                        random_state=42, verbose=-1),
            "params": {
                "n_estimators":  [100, 200, 300],
                "learning_rate": [0.01, 0.05, 0.1],
                "num_leaves":    [20, 31, 50],
                "max_depth":     [5, 8, 10]
            }
        },
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=1000),
            "params": {
                "C": [0.01, 0.1, 1.0, 10.0],
                "solver": ["lbfgs", "saga"]
            }
        }
    }

    best_f1, best_name, best_model = -1, None, None

    for name, config in param_grids.items():
        print(f"\n{'─'*50}")
        print(f"  Tuning {name}...")

        search = RandomizedSearchCV(
            config["model"],
            config["params"],
            n_iter=10,
            cv=3,
            scoring="f1_macro",
            random_state=42,
            n_jobs=-1
        )
        search.fit(X_train_bal, y_train_bal)

        best  = search.best_estimator_
        preds = best.predict(X_test_sc)

        acc = accuracy_score(y_test, preds)
        f1  = f1_score(y_test, preds,
                       average="macro", zero_division=0)

        print(f"  Best Params: {search.best_params_}")
        print(f"  Accuracy: {acc:.4f}   Macro F1: {f1:.4f}")
        print(classification_report(y_test, preds,
              target_names=LABEL_NAMES, zero_division=0))

        if f1 > best_f1:
            best_f1, best_name, best_model = f1, name, best

    # Save best model
    print(f"\n{'═'*50}")
    print(f"  Best Model: {best_name}  (Macro F1 = {best_f1:.4f})")
    print(f"{'═'*50}")
    joblib.dump(best_model,  "models/buy_sell_classifier.pkl")
    joblib.dump(scaler,      "models/scaler.pkl")
    joblib.dump(FEATURE_COLS,"models/feature_cols.pkl")
    print("Model saved to models/")

    return best_name, test_df, X_test_sc, y_test


if __name__ == "__main__":
    df = pd.read_csv(
        "data/processed/BTCUSDT_labeled.csv",
        index_col="open_time"
    )
    print("Starting training pipeline...")
    print(f"Dataset: {len(df)} rows, {len(df.columns)} columns")
    tune_and_train(df)