#!/bin/bash
# Run at Render startup — trains the model then starts the server
set -e
echo "=== CryptoSense DSS Startup ==="

# Move to project root so src/ is importable
cd /opt/render/project/src

echo "Training model on live Binance data..."
python train_model.py

echo "Starting gunicorn server..."
cd backend
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
