#!/usr/bin/env python3
"""
Simple script to view data from the SQLite database.
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from ai_core.core.config import settings

def view_data():
    """Connect to database and print tables."""
    
    # Use the SQLite URL directly for this viewer
    db_url = "sqlite:///./trading.db"
    print(f"📊 Connecting to database: {db_url}")
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # 1. View Strategies
        print("\n" + "="*80)
        print("♟️  STRATEGIES")
        print("="*80)
        try:
            strategies = pd.read_sql("SELECT * FROM strategies", conn)
            if not strategies.empty:
                print(strategies[['id', 'name', 'is_active', 'total_trades', 'total_pnl']].to_string(index=False))
            else:
                print("No strategies found.")
        except Exception as e:
            print(f"Error reading strategies: {e}")

        # 2. View Trades
        print("\n" + "="*80)
        print("📈 TRADES")
        print("="*80)
        try:
            trades = pd.read_sql("SELECT * FROM trades ORDER BY id DESC LIMIT 10", conn)
            if not trades.empty:
                # Select key columns for display
                cols = ['id', 'symbol', 'action', 'quantity', 'entry_price', 'status', 'pnl', 'entry_time']
                print(trades[cols].to_string(index=False))
            else:
                print("No trades found.")
        except Exception as e:
            print(f"Error reading trades: {e}")

        # 3. View AI Signals (Rejected/Logged)
        print("\n" + "="*80)
        print("🤖 AI SIGNALS (Rejected/Logged)")
        print("="*80)
        try:
            signals = pd.read_sql("SELECT * FROM ai_signals ORDER BY id DESC LIMIT 10", conn)
            if not signals.empty:
                cols = ['id', 'symbol', 'signal_type', 'confidence', 'price', 'timestamp', 'is_executed']
                print(signals[cols].to_string(index=False))
            else:
                print("No signals found.")
        except Exception as e:
            print(f"Error reading signals: {e}")

if __name__ == "__main__":
    view_data()
