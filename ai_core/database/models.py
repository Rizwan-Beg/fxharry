from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    strategy_type = Column(String(50))  # 'python', 'cpp', 'ml_model'
    file_path = Column(String(255))
    parameters = Column(JSON)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    trades = relationship("Trade", back_populates="strategy")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    symbol = Column(String(10), index=True)  # EURUSD, GBPUSD, etc.
    action = Column(String(10))  # BUY, SELL
    quantity = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    pnl = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)
    status = Column(String(20), default='OPEN')  # OPEN, CLOSED, CANCELLED
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    
    # Execution tracking
    broker_order_id = Column(String(50), index=True, nullable=True)
    order_status = Column(String(20), nullable=True)  # PENDING, SUBMITTED, FILLED, etc.
    submitted_time = Column(DateTime, nullable=True)
    filled_time = Column(DateTime, nullable=True)
    execution_mode = Column(String(20), nullable=True)  # PAPER, LIVE
    rejection_reason = Column(Text, nullable=True)
    
    # Risk metrics
    risk_score = Column(Float, default=0.0)
    position_size_percent = Column(Float, default=0.0)
    risk_assessment = Column(JSON, nullable=True)  # Store full risk check results
    
    strategy = relationship("Strategy", back_populates="trades")

class BacktestResult(Base):
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_capital = Column(Float)
    final_capital = Column(Float)
    total_return = Column(Float)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    avg_trade_duration = Column(Float)  # in hours
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Detailed results
    trade_history = Column(JSON)
    equity_curve = Column(JSON)
    monthly_returns = Column(JSON)

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    timestamp = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float, default=0.0)
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)

class AISignal(Base):
    __tablename__ = "ai_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    symbol = Column(String(10))
    signal_type = Column(String(10))  # BUY, SELL, HOLD
    confidence = Column(Float)  # 0.0 to 1.0
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    features = Column(JSON)  # AI model input features
    model_output = Column(JSON)  # Raw model output
    is_executed = Column(Boolean, default=False)
    execution_trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)  # Link to actual trade
    execution_time = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

class AccountSnapshot(Base):
    __tablename__ = "account_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    total_equity = Column(Float)
    available_funds = Column(Float)
    buying_power = Column(Float)
    gross_position_value = Column(Float)
    realized_pnl = Column(Float)
    unrealized_pnl = Column(Float)
    day_trades_remaining = Column(Integer)
    positions = Column(JSON)  # Current positions