# Quick Start Guide

## Prerequisites

- Python 3.8+
- pip or conda
- Git
- A Supabase account

## Quick Setup (5 minutes)

### 1. Clone/Setup Project

```bash
cd btc-ml-project
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Update .env File

Already created with placeholder values. Keep Supabase credentials secure.

### 4. Create Database Tables

Log into Supabase dashboard and create these tables:

**users table:**

```sql
create table users (
    id uuid primary key references auth.users(id),
    email text unique not null,
    name text,
    created_at timestamp default now()
);
```

**trading_history table:**

```sql
create table trading_history (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references users(id),
    symbol text,
    signal text,
    price numeric,
    created_at timestamp default now()
);
```

**backtest_results table:**

```sql
create table backtest_results (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references users(id),
    symbol text,
    ml_strategy_value numeric,
    outperformance_pct numeric,
    created_at timestamp default now()
);
```

### 5. Start Backend

```bash
cd backend
python app.py
```

Backend runs on `http://localhost:5000`

### 6. Start Frontend (New Terminal)

```bash
cd frontend
python server.py
```

Frontend runs on `http://localhost:8000`

### 7. Open Application

Go to `http://localhost:8000` in your browser

## Default Login Flow

1. **Register Page** → Create new account
2. **Login Page** → Enter credentials
3. **Verification Page** → Check terminal for verification code
4. **Dashboard** → Start analyzing!

## API Usage Examples

### Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com","password":"pass123"}'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"pass123"}'
```

### Get Predictions

```bash
curl -X POST http://localhost:5000/api/predictions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"symbol":"BTCUSDT","interval":"1d"}'
```

## Project Structure

```
btc-ml-project/
├── backend/
│   ├── app.py              # Main API
│   ├── config.py           # Configuration
│   ├── database.py         # DB schema
│   ├── models/             # ML models folder
│   └── requirements.txt
├── frontend/
│   ├── index.html          # Login page
│   ├── dashboard.html      # Main dashboard
│   ├── server.py           # Dev server
│   ├── config.py           # Frontend config
│   └── requirements.txt
├── .env                    # Environment variables
├── .gitignore
└── README.md
```

## Key Features

✅ User Registration & Login
✅ Email Verification
✅ JWT Authentication
✅ Real-time ML Predictions
✅ Backtest Simulations
✅ Responsive Dark Theme
✅ Technical Indicators (RSI, MACD)
✅ Fear & Greed Index
✅ Trading History
✅ Performance Metrics

## Next Steps

1. **Regenerate API Keys** (yours are exposed)
2. **Configure Email Service** (SendGrid, AWS SES, etc.)
3. **Move ML Models** to `backend/models/`
4. **Update API Paths** in `backend/app.py` if needed
5. **Test All Features**
6. **Deploy to Production**

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### CORS Error

- Backend has CORS enabled
- Check browser console for detailed errors

### Database Connection Error

- Verify Supabase URL and key in .env
- Check network connection
- Ensure tables are created

### JWT Token Expired

- Login again to get new token
- Token expires in 30 days

## Documentation

- [README.md](./README.md) - Full documentation
- [Backend API](./backend/app.py) - API endpoints
- [Frontend](./frontend/index.html) - UI code
- [Supabase Docs](https://supabase.com/docs)
- [Flask Docs](https://flask.palletsprojects.com/)

Enjoy! 🚀
