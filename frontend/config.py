"""
Frontend configuration and utilities
"""

API_URL = 'http://localhost:5000'

# Feature flags
ENABLE_BACKTEST = True
ENABLE_EMAIL_VERIFICATION = True

# UI Configuration
THEME = {
    'primary_color': '#f0b429',
    'background': '#0b0c10',
    'surface': '#0d0e14',
    'border': '#1e2030',
    'text_primary': '#e6edf3',
    'text_secondary': '#6b7280',
    'text_muted': '#4b5563',
    'success': '#3fb950',
    'error': '#f85149',
    'warning': '#e6b430'
}

# Assets
ASSETS = {
    'logo': '₿',
    'app_name': 'CryptoSense DSS',
    'app_subtitle': 'DECISION SUPPORT SYSTEM'
}

# Supported trading pairs
TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']

# Timeframes
TIMEFRAMES = ['1h', '4h', '1d']

# Signal thresholds
SIGNAL_THRESHOLD_MIN = 1
SIGNAL_THRESHOLD_MAX = 5
SIGNAL_THRESHOLD_DEFAULT = 2
