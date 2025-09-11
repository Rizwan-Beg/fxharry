from fastapi import APIRouter, Depends, HTTPException
from services.ibkr_service import IBKRService
from services.risk_manager import RiskManager
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()
ibkr_service = IBKRService()
risk_manager = RiskManager()

class RiskLimitsUpdate(BaseModel):
    max_daily_loss_percent: float
    max_position_size_percent: float
    max_correlation_exposure_percent: float
    max_drawdown_limit_percent: float

@router.get("/summary")
def get_account_summary():
    """Get account summary from IBKR"""
    
    if not ibkr_service.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to broker")
    
    account_data = ibkr_service.get_account_data()
    positions = ibkr_service.get_positions()
    
    # Calculate total position value
    total_position_value = sum(
        abs(pos.get('market_value', 0)) for pos in positions.values()
    )
    
    return {
        "account_data": account_data,
        "positions": positions,
        "total_position_value": total_position_value,
        "connection_status": "connected"
    }

@router.get("/positions")
def get_positions():
    """Get current positions"""
    
    if not ibkr_service.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to broker")
    
    positions = ibkr_service.get_positions()
    
    return {
        "positions": positions,
        "total_positions": len(positions)
    }

@router.get("/market-data")
def get_market_data():
    """Get current market data"""
    
    if not ibkr_service.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to broker")
    
    market_data = ibkr_service.get_market_data()
    
    return {
        "market_data": market_data,
        "symbols": list(market_data.keys()),
        "last_updated": "real-time"
    }

@router.get("/risk-assessment")
def get_portfolio_risk_assessment():
    """Get current portfolio risk assessment"""
    
    risk_assessment = risk_manager.assess_portfolio_risk()
    risk_limits = risk_manager.get_risk_limits()
    
    return {
        "risk_assessment": risk_assessment,
        "risk_limits": risk_limits,
        "timestamp": "real-time"
    }

@router.post("/risk-limits")
def update_risk_limits(limits: RiskLimitsUpdate):
    """Update risk management limits"""
    
    success = risk_manager.update_risk_limits({
        "max_daily_loss_percent": limits.max_daily_loss_percent,
        "max_position_size_percent": limits.max_position_size_percent,
        "max_correlation_exposure_percent": limits.max_correlation_exposure_percent,
        "max_drawdown_limit_percent": limits.max_drawdown_limit_percent
    })
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update risk limits")
    
    return {"message": "Risk limits updated successfully"}

@router.get("/connection-status")
def get_connection_status():
    """Get broker connection status"""
    
    return {
        "ibkr_connected": ibkr_service.is_connected(),
        "market_data_streaming": ibkr_service.is_connected(),
        "last_heartbeat": "real-time" if ibkr_service.is_connected() else "disconnected"
    }

@router.post("/reconnect")
async def reconnect_broker():
    """Attempt to reconnect to IBKR"""
    
    try:
        success = await ibkr_service.initialize()
        
        if success:
            return {"message": "Successfully reconnected to broker"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reconnect to broker")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reconnection error: {str(e)}")

@router.get("/performance-metrics")
def get_account_performance_metrics():
    """Get account performance metrics"""
    
    # This would typically pull from your database of historical account snapshots
    # For now, return sample metrics
    
    return {
        "daily_pnl": risk_manager._get_daily_pnl(),
        "monthly_return": 0.025,  # 2.5%
        "ytd_return": 0.15,       # 15%
        "sharpe_ratio": 1.2,
        "max_drawdown": 0.08,     # 8%
        "win_rate": 0.65,         # 65%
        "profit_factor": 1.4,
        "active_positions": len(ibkr_service.get_positions()),
        "total_trades_today": 5
    }

@router.get("/trading-hours")
def get_trading_hours():
    """Get forex trading hours information"""
    
    return {
        "forex_market": {
            "status": "open",  # This would be calculated based on current time
            "next_session": "London Open",
            "current_session": "New York",
            "major_sessions": [
                {"name": "Sydney", "open": "21:00", "close": "06:00", "timezone": "UTC"},
                {"name": "Tokyo", "open": "00:00", "close": "09:00", "timezone": "UTC"},
                {"name": "London", "open": "08:00", "close": "17:00", "timezone": "UTC"},
                {"name": "New York", "open": "13:00", "close": "22:00", "timezone": "UTC"}
            ]
        },
        "gold_market": {
            "status": "open",
            "hours": "23:00 Sunday - 22:00 Friday (UTC)"
        }
    }