"""
Database initialization and schema setup
"""

def init_supabase_db(supabase_client):
    """Initialize Supabase database tables"""
    
    # Users table (auto-created by Supabase Auth, but here's the schema)
    users_schema = """
    create table if not exists users (
        id uuid primary key references auth.users(id) on delete cascade,
        email text unique not null,
        name text,
        avatar_url text,
        created_at timestamp with time zone default current_timestamp,
        updated_at timestamp with time zone default current_timestamp
    );
    """
    
    # Trading history table
    trading_history_schema = """
    create table if not exists trading_history (
        id uuid primary key default uuid_generate_v4(),
        user_id uuid not null references users(id) on delete cascade,
        symbol text not null,
        interval text not null,
        signal text not null,
        price numeric,
        rsi numeric,
        macd numeric,
        fear_greed_value integer,
        created_at timestamp with time zone default current_timestamp
    );
    """
    
    # Backtest results table
    backtest_results_schema = """
    create table if not exists backtest_results (
        id uuid primary key default uuid_generate_v4(),
        user_id uuid not null references users(id) on delete cascade,
        symbol text not null,
        ml_strategy_value numeric,
        buy_hold_value numeric,
        ml_return_pct numeric,
        buy_hold_return_pct numeric,
        outperformance_pct numeric,
        trades integer,
        created_at timestamp with time zone default current_timestamp
    );
    """
    
    return {
        'users': users_schema,
        'trading_history': trading_history_schema,
        'backtest_results': backtest_results_schema
    }
