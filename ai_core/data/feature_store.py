import sqlite3
import json
import os
from datetime import datetime

class FeatureStore:
    """
    SQLite-based feature store for logging trade signals, context, and outcomes.
    This builds a proprietary dataset for future machine learning.
    """
    def __init__(self, db_path: str = "features.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trade_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    price REAL NOT NULL,
                    
                    -- Environment/Context
                    regime TEXT,
                    adx REAL,
                    atr REAL,
                    session TEXT,
                    session_score INTEGER,
                    llm_macro_score INTEGER,
                    
                    -- Technicals & Final Score
                    technical_score INTEGER,
                    total_score INTEGER,
                    passed_threshold BOOLEAN,
                    
                    -- Raw features dumped as JSON for flexibility
                    raw_features JSON,
                    
                    -- Outcome (to be updated later)
                    outcome_pnl REAL,
                    outcome_label INTEGER -- 1 for win, 0 for loss
                )
            ''')
            conn.commit()

    def log_signal(self, 
                   symbol: str, 
                   strategy_id: str, 
                   action: str, 
                   price: float,
                   regime_data: dict,
                   session_name: str,
                   session_score: int,
                   llm_score: int,
                   technical_score: int,
                   total_score: int,
                   passed: bool,
                   raw_features: dict):
        """
        Log a generated signal with all its environmental context to the SQLite DB.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trade_features (
                        timestamp, symbol, strategy_id, action, price,
                        regime, adx, atr, session, session_score, llm_macro_score,
                        technical_score, total_score, passed_threshold, raw_features
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.utcnow().isoformat(),
                    symbol,
                    strategy_id,
                    action,
                    price,
                    regime_data.get('regime'),
                    regime_data.get('adx'),
                    regime_data.get('atr'),
                    session_name,
                    session_score,
                    llm_score,
                    technical_score,
                    total_score,
                    int(passed),
                    json.dumps(raw_features)
                ))
                conn.commit()
        except Exception as e:
            # We don't want DB errors to crash the live trading loop
            print(f"Error logging to feature store: {e}")
