from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database.database import get_db
from ...database.models import Trade
from ...services.broker.ibkr_service import IBKRService
from ...services.risk_manager.risk_manager import RiskManager
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
ibkr_service = IBKRService()
risk_manager = RiskManager()

class TradeRequest(BaseModel):
    symbol: str
    action: str  # BUY or SELL
    quantity: float
    order_type: str = "MKT"  # MKT, LMT
    limit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_id: Optional[int] = None

@router.post("/", response_model=dict)
async def create_trade(trade_request: TradeRequest, db: Session = Depends(get_db)):
    """Execute a new trade"""
    
    # Risk assessment
    account_data = ibkr_service.get_account_data()
    account_value = float(account_data.get('NetLiquidation', {}).get('value', 100000))
    
    risk_assessment = risk_manager.assess_trade_risk(
        symbol=trade_request.symbol,
        action=trade_request.action,
        quantity=trade_request.quantity,
        entry_price=trade_request.limit_price or 1.0,  # Use current market price in production
        account_value=account_value
    )
    
    if not risk_assessment['approved']:
        raise HTTPException(
            status_code=400, 
            detail=f"Trade rejected by risk management: {', '.join(risk_assessment['warnings'])}"
        )
    
    # Place order with IBKR
    order_response = await ibkr_service.place_order(
        symbol=trade_request.symbol,
        action=trade_request.action,
        quantity=trade_request.quantity,
        order_type=trade_request.order_type,
        limit_price=trade_request.limit_price,
        stop_loss=trade_request.stop_loss,
        take_profit=trade_request.take_profit
    )
    
    if not order_response:
        raise HTTPException(status_code=500, detail="Failed to place order with broker")
    
    # Create trade record
    db_trade = Trade(
        strategy_id=trade_request.strategy_id,
        symbol=trade_request.symbol,
        action=trade_request.action,
        quantity=trade_request.quantity,
        entry_price=trade_request.limit_price or 0.0,  # Will be updated when filled
        stop_loss=trade_request.stop_loss,
        take_profit=trade_request.take_profit,
        risk_score=risk_assessment['risk_score'],
        position_size_percent=risk_assessment['position_size_percent']
    )
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    return {
        "trade_id": db_trade.id,
        "order": order_response,
        "message": "Trade executed successfully",
        "risk_assessment": risk_assessment
    }

@router.get("/", response_model=List[dict])
def get_trades(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    strategy_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get trades with optional filters"""
    
    query = db.query(Trade)
    
    if status:
        query = query.filter(Trade.status == status)
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    
    if strategy_id:
        query = query.filter(Trade.strategy_id == strategy_id)
    
    trades = query.order_by(Trade.entry_time.desc()).limit(limit).all()
    
    return [
        {
            "id": trade.id,
            "strategy_id": trade.strategy_id,
            "symbol": trade.symbol,
            "action": trade.action,
            "quantity": trade.quantity,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "pnl": trade.pnl,
            "commission": trade.commission,
            "status": trade.status,
            "entry_time": trade.entry_time.isoformat(),
            "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "risk_score": trade.risk_score
        }
        for trade in trades
    ]

@router.get("/{trade_id}", response_model=dict)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get specific trade details"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return {
        "id": trade.id,
        "strategy_id": trade.strategy_id,
        "symbol": trade.symbol,
        "action": trade.action,
        "quantity": trade.quantity,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "pnl": trade.pnl,
        "commission": trade.commission,
        "status": trade.status,
        "entry_time": trade.entry_time.isoformat(),
        "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
        "stop_loss": trade.stop_loss,
        "take_profit": trade.take_profit,
        "risk_score": trade.risk_score,
        "position_size_percent": trade.position_size_percent
    }

@router.put("/{trade_id}/close")
async def close_trade(trade_id: int, db: Session = Depends(get_db)):
    """Manually close an open trade"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade.status != 'OPEN':
        raise HTTPException(status_code=400, detail="Trade is not open")
    
    # Get current market price
    market_data = ibkr_service.get_market_data()
    if trade.symbol not in market_data:
        raise HTTPException(status_code=400, detail="Market data not available")
    
    current_price = market_data[trade.symbol]['last']
    
    # Place closing order
    closing_action = 'SELL' if trade.action == 'BUY' else 'BUY'
    order_response = await ibkr_service.place_order(
        symbol=trade.symbol,
        action=closing_action,
        quantity=trade.quantity,
        order_type='MKT'
    )
    
    if not order_response:
        raise HTTPException(status_code=500, detail="Failed to close trade")
    
    # Update trade record
    trade.exit_price = current_price
    trade.exit_time = datetime.utcnow()
    trade.status = 'CLOSED'
    
    # Calculate P&L
    if trade.action == 'BUY':
        trade.pnl = (current_price - trade.entry_price) * trade.quantity
    else:
        trade.pnl = (trade.entry_price - current_price) * trade.quantity
    
    db.commit()
    
    return {
        "message": "Trade closed successfully",
        "pnl": trade.pnl,
        "exit_price": current_price
    }

@router.get("/analytics/summary")
def get_trading_summary(db: Session = Depends(get_db)):
    """Get trading analytics summary"""
    
    # All trades
    all_trades = db.query(Trade).all()
    closed_trades = [t for t in all_trades if t.status == 'CLOSED']
    open_trades = [t for t in all_trades if t.status == 'OPEN']
    
    if not closed_trades:
        return {
            "total_trades": len(all_trades),
            "open_trades": len(open_trades),
            "closed_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl_per_trade": 0
        }
    
    # Calculate metrics
    winning_trades = len([t for t in closed_trades if t.pnl > 0])
    total_pnl = sum(t.pnl for t in closed_trades)
    avg_pnl = total_pnl / len(closed_trades)
    win_rate = winning_trades / len(closed_trades)
    
    # Recent performance (last 30 days)
    thirty_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    recent_trades = [t for t in closed_trades if t.entry_time >= thirty_days_ago]
    recent_pnl = sum(t.pnl for t in recent_trades) if recent_trades else 0
    
    return {
        "total_trades": len(all_trades),
        "open_trades": len(open_trades),
        "closed_trades": len(closed_trades),
        "winning_trades": winning_trades,
        "losing_trades": len(closed_trades) - winning_trades,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "avg_pnl_per_trade": avg_pnl,
        "recent_pnl_30d": recent_pnl,
        "recent_trades_30d": len(recent_trades)
    }

@router.post("/calculate-position-size")
def calculate_position_size(
    symbol: str,
    entry_price: float,
    stop_loss: float,
    risk_percent: float = 1.0,
    db: Session = Depends(get_db)
):
    """Calculate optimal position size for a trade"""
    
    # Get account value
    account_data = ibkr_service.get_account_data()
    account_value = float(account_data.get('NetLiquidation', {}).get('value', 100000))
    
    result = risk_manager.calculate_position_size(
        symbol=symbol,
        entry_price=entry_price,
        stop_loss=stop_loss,
        risk_percent=risk_percent / 100,
        account_value=account_value
    )
    
    return result