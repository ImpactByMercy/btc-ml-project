# CryptoSense DSS - Modernized Application

## Project Structure

```
btc-ml-project/
├── backend/                    # Flask API backend
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   ├── database.py            # Database schema definitions
│   ├── requirements.txt        # Backend dependencies
│   └── models/                # ML models (move here)
│
├── frontend/                  # Frontend (HTML/CSS/JS)
│   ├── index.html            # Login & Register page
│   ├── dashboard.html        # Main dashboard
│   ├── server.py             # Frontend dev server
│   ├── src/                  # Source files (keep for reference)
│   └── requirements.txt        # Frontend dependencies (if using Streamlit)
│
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## Setup Instructions

### 1. Install Dependencies

**Backend:**

```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**

```bash
cd frontend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file at the root contains:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `SUPABASE_DB_URL`: Your Supabase PostgreSQL connection string
- `SECRET_KEY`: Flask secret key (change for production)
- `JWT_SECRET`: JWT signing secret (change for production)

⚠️ **SECURITY WARNING**: The credentials provided are now exposed. Please regenerate your Supabase API keys immediately.

### 3. Set up Supabase Database

1. Go to your Supabase dashboard
2. Create tables using the schema in `backend/database.py`:
   - `users` - User profiles
   - `trading_history` - Trading signals history
   - `backtest_results` - Backtest simulation results

3. Enable Row Level Security (RLS) policies for user data protection

### 4. Run the Application

**Terminal 1 - Backend API:**

```bash
cd backend
python app.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Frontend Dev Server:**

```bash
cd frontend
python server.py
# Server runs on http://localhost:8000
# Open http://localhost:8000 in your browser
```

## Features

### Authentication Flow

1. **Register**: Create new account with email and password
2. **Login**: Enter credentials
3. **Email Verification**: 6-digit code sent to email
4. **Dashboard Access**: After successful verification

### Dashboard

- **Asset Selection**: BTCUSDT, ETHUSDT, BNBUSDT
- **Timeframe Selection**: 1h, 4h, 1d
- **Signal Threshold**: Adjustable 1-5%
- **Analysis**: Real-time ML predictions
- **Backtest**: Simulate trading strategy performance
- **Metrics**: RSI, Fear & Greed Index, MACD signals

### API Endpoints

#### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and send verification code
- `POST /api/auth/verify` - Verify email code

#### User

- `GET /api/user/profile` - Get user profile (requires token)

#### Analysis

- `POST /api/predictions` - Get ML predictions (requires token)
- `POST /api/backtest` - Run backtest simulation (requires token)

## Technology Stack

### Backend

- **Framework**: Flask
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + JWT
- **ML Models**: XGBoost, scikit-learn
- **Data**: Binance API, Fear & Greed Index

### Frontend

- **HTML5/CSS3**: Custom dark theme
- **JavaScript**: Vanilla JS (no dependencies)
- **Authentication**: JWT tokens
- **API Communication**: Fetch API

## Deployment

### Backend (Flask)

```bash
# For production, use a WSGI server like Gunicorn
pip install gunicorn
gunicorn app:app
```

### Frontend

- Deploy to static hosting (Vercel, Netlify, GitHub Pages)
- Or use a simple HTTP server for production

## Environment Variables for Production

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<strong-random-key>
JWT_SECRET=<strong-random-key>
SUPABASE_URL=<your-url>
SUPABASE_KEY=<your-key>
SUPABASE_DB_URL=<your-db-url>
```

## Testing the Application

1. **Register**:
   - Fill in name, email, password on register form
   - Submit and switch to login

2. **Login**:
   - Enter email and password
   - Verification code will be sent (check console in dev)

3. **Verify**:
   - Enter the 6-digit code shown in console
   - Redirected to dashboard

4. **Analysis**:
   - Select asset, timeframe, threshold
   - Click "Run Analysis"
   - View ML signal and metrics

5. **Backtest**:
   - Click "Run Backtest"
   - View strategy vs Buy & Hold comparison

## Troubleshooting

### CORS Errors

- Backend CORS is enabled for all origins in development
- For production, update `CORS(app)` to specific domains

### Authentication Failures

- Check Supabase connection string in `.env`
- Ensure Supabase tables exist with correct schema
- Verify JWT secrets are set

### Model Loading Errors

- Ensure ML model files exist in `backend/models/`
- Check file paths are correct in `app.py`

## Security Considerations

1. **Regenerate API Keys**: Your Supabase keys are exposed. Regenerate immediately.
2. **Environment Variables**: Never commit `.env` to git
3. **CORS**: Restrict to specific domains in production
4. **JWT**: Use strong, random secrets for production
5. **HTTPS**: Always use HTTPS in production
6. **Input Validation**: Add more thorough validation for production
7. **Rate Limiting**: Implement rate limiting on API endpoints

## Next Steps

1. Regenerate Supabase API keys
2. Implement email service for verification codes (SendGrid, AWS SES, etc.)
3. Add more security features (2FA, password reset, etc.)
4. Implement caching for frequently accessed data
5. Add unit and integration tests
6. Set up CI/CD pipeline
7. Deploy to cloud platform (Heroku, Railway, AWS, etc.)

## Support

For issues or questions, refer to:

- [Supabase Documentation](https://supabase.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
