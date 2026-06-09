import os
import sys
from pathlib import Path

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import supabase
from supabase import create_client, Client
import secrets
from email_service import send_verification_email

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

verification_codes = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing authentication token'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
            user_id = data['user_id']
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(user_id, *args, **kwargs)
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400

    try:
        response = supabase_client.auth.sign_up({'email': email, 'password': password})
        user_id = response.user.id

        try:
            supabase_client.table('users').upsert({
                'id': user_id,
                'email': email,
                'name': name,
                'created_at': datetime.now(timezone.utc).isoformat()
            }, on_conflict='id').execute()
        except Exception as profile_error:
            print(f"Profile insert warning: {profile_error}")

        return jsonify({
            'message': 'User registered successfully. Please check your email to confirm.',
            'user_id': user_id,
            'email': email
        }), 201
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400

    try:
        response = supabase_client.auth.sign_in_with_password({'email': email, 'password': password})
        user_id = response.user.id

        code = secrets.token_hex(3)
        verification_codes[user_id] = {
            'code': code,
            'email': email,
            'timestamp': datetime.now(timezone.utc)
        }

        print(f"\n✓ Verification code for {email}: {code}\n")
        send_verification_email(email, code)

        return jsonify({
            'message': 'Verification code sent to email',
            'user_id': user_id,
            'session_token': response.session.access_token if response.session else None,
            'dev_code': code
        }), 200
    except Exception as e:
        error_msg = str(e)
        print(f"Login error: {error_msg}")
        if 'Invalid login credentials' in error_msg:
            return jsonify({'message': 'Invalid email or password'}), 401
        elif 'Email not confirmed' in error_msg:
            return jsonify({'message': 'Please confirm your email first. Check your inbox.'}), 401
        else:
            return jsonify({'message': f'Login failed: {error_msg}'}), 401

@app.route('/api/auth/verify', methods=['POST'])
def verify_code():
    data = request.json
    user_id = data.get('user_id')
    code = data.get('code')

    if user_id not in verification_codes:
        return jsonify({'message': 'No verification code found'}), 400

    if verification_codes[user_id]['code'] != code:
        return jsonify({'message': 'Invalid verification code'}), 400

    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=30)
    }, app.config['JWT_SECRET'], algorithm='HS256')

    del verification_codes[user_id]

    return jsonify({'message': 'Email verified successfully', 'token': token}), 200

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(user_id):
    try:
        response = supabase_client.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            return jsonify(response.data[0]), 200
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/api/predictions', methods=['POST'])
@token_required
def get_predictions(user_id):
    data = request.json
    symbol = data.get('symbol', 'BTCUSDT')
    interval = data.get('interval', '1d')

    try:
        from src.data_fetcher import fetch_binance
        from src.feature_generator import engineer_features
        from src.sentiment import fetch_fear_greed, merge_fear_greed
        from src.labeler import generate_labels
        import joblib

        df = fetch_binance(symbol, interval, 500)
        df = engineer_features(df)

        try:
            fg = fetch_fear_greed(500)
            df = merge_fear_greed(df, fg)
        except:
            df["fear_greed_value"] = 50

        df = generate_labels(df, buy_threshold=0.02, sell_threshold=-0.02)

        models_dir = Path(__file__).parent / 'models'
        model_path     = models_dir / 'buy_sell_classifier.pkl'
        scaler_path    = models_dir / 'scaler.pkl'
        feat_cols_path = models_dir / 'feature_cols.pkl'

        if not model_path.exists():
            return jsonify({'message': f'Model file not found: {model_path}'}), 400

        model     = joblib.load(str(model_path))
        scaler    = joblib.load(str(scaler_path))
        feat_cols = joblib.load(str(feat_cols_path))

        cols  = [c for c in feat_cols if c in df.columns]
        clean = df[cols].dropna()
        X     = scaler.transform(clean.values)
        preds = model.predict(X)

        latest_signal = ["SELL", "HOLD", "BUY"][int(preds[-1])]

        return jsonify({
            'symbol': symbol,
            'interval': interval,
            'signal': latest_signal,
            'price': float(df['close'].iloc[-1]),
            'rsi': float(df['rsi'].iloc[-1]),
            'macd': float(df['macd_diff'].iloc[-1]),
            'fear_greed': int(df['fear_greed_value'].iloc[-1])
        }), 200
    except Exception as e:
        return jsonify({'message': str(e), 'error_type': type(e).__name__}), 400

@app.route('/api/backtest', methods=['POST'])
@token_required
def backtest(user_id):
    data = request.json
    symbol = data.get('symbol', 'BTCUSDT')

    try:
        from src.data_fetcher import fetch_binance
        from src.feature_generator import engineer_features
        from src.sentiment import fetch_fear_greed, merge_fear_greed
        from src.labeler import generate_labels
        import joblib

        df = fetch_binance(symbol, '1d', 500)
        df = engineer_features(df)

        try:
            fg = fetch_fear_greed(200)
            df = merge_fear_greed(df, fg)
        except:
            df["fear_greed_value"] = 50

        df = generate_labels(df, buy_threshold=0.02, sell_threshold=-0.02)

        models_dir = Path(__file__).parent / 'models'
        model_path     = models_dir / 'buy_sell_classifier.pkl'
        scaler_path    = models_dir / 'scaler.pkl'
        feat_cols_path = models_dir / 'feature_cols.pkl'

        if not model_path.exists():
            return jsonify({'message': f'Model file not found: {model_path}'}), 400

        model     = joblib.load(str(model_path))
        scaler    = joblib.load(str(scaler_path))
        feat_cols = joblib.load(str(feat_cols_path))

        cols  = [c for c in feat_cols if c in df.columns]
        clean = df[cols].dropna()
        X     = scaler.transform(clean.values)
        preds = model.predict(X)

        signals = [["SELL", "HOLD", "BUY"][int(x)] for x in preds]
        prices  = clean['close'].values

        initial  = 10000.0
        cash     = initial
        holdings = 0.0
        portfolio = []
        trades   = 0

        for i, price in enumerate(prices):
            sig = signals[i]
            if sig == "BUY" and holdings == 0:
                holdings = cash / price
                cash = 0.0
                trades += 1
            elif sig == "SELL" and holdings > 0:
                cash = holdings * price
                holdings = 0.0
                trades += 1
            portfolio.append(cash + holdings * price)

        final_s = portfolio[-1] if portfolio else initial
        final_b = (initial / prices[0]) * prices[-1]
        ret_s   = (final_s - initial) / initial * 100
        ret_b   = (final_b - initial) / initial * 100

        return jsonify({
            'symbol': symbol,
            'ml_strategy_value': float(final_s),
            'buy_hold_value': float(final_b),
            'ml_return_pct': float(ret_s),
            'buy_hold_return_pct': float(ret_b),
            'outperformance_pct': float(ret_s - ret_b),
            'trades': trades
        }), 200
    except Exception as e:
        return jsonify({'message': str(e), 'error_type': type(e).__name__}), 400

def send_verification_email(email, code):
    from email_service import send_verification_email as email_send
    return email_send(email, code)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
