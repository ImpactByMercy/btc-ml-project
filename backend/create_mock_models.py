#!/usr/bin/env python
"""Create mock ML models for testing the predictions endpoint."""

import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

# Create models directory
models_dir = Path(__file__).parent / 'models'
models_dir.mkdir(exist_ok=True)

# Create dummy model
print("Creating mock ML models...")
model = RandomForestClassifier(n_estimators=10, random_state=42)
X_dummy = np.random.rand(100, 20)
y_dummy = np.random.randint(0, 3, 100)
model.fit(X_dummy, y_dummy)

# Create dummy scaler
scaler = StandardScaler()
scaler.fit(X_dummy)

# Feature columns
feature_cols = [
    'open', 'high', 'low', 'close', 'volume', 'rsi', 'macd', 'macd_signal',
    'macd_diff', 'bb_upper', 'bb_lower', 'bb_middle', 'fear_greed_value',
    'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'momentum', 'price_change'
]

# Save files
joblib.dump(model, models_dir / 'buy_sell_classifier.pkl')
joblib.dump(scaler, models_dir / 'scaler.pkl')
joblib.dump(feature_cols, models_dir / 'feature_cols.pkl')

print(f'✓ Mock ML models created in {models_dir}')
print(f'  - buy_sell_classifier.pkl')
print(f'  - scaler.pkl')
print(f'  - feature_cols.pkl')
