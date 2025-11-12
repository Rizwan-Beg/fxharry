from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database.database import get_db
from ...services.backtesting.engine import BacktestingEngine
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()
backtesting_engine = BacktestingEngine()

class BacktestRequest(BaseModel):
    strategy_id: int
    start_date: str  # ISO format
    end_date: str    # ISO format
    initial_capital: float = 100000
    symbols: Optional[List[str]] = ['EURUSD', 'GBPUSD', 'XAUUSD']

@router.post("/run")
async def run_backtest(request: BacktestRequest, db: Session = Depends(get_db)):
    """Run a backtest for a strategy"""
    
    try:
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format.")
    
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if request.initial_capital <= 0:
        raise HTTPException(status_code=400, detail="Initial capital must be positive")
    
    results = await backtesting_engine.run_backtest(
        strategy_id=request.strategy_id,
        start_date=start_date,
        end_date=end_date,
        initial_capital=request.initial_capital,
        symbols=request.symbols
    )
    
    if 'error' in results:
        raise HTTPException(status_code=400, detail=results['error'])
    
    return results

@router.get("/results/{strategy_id}")
async def get_backtest_results(strategy_id: int):
    """Get historical backtest results for a strategy"""
    
    results = await backtesting_engine.get_backtest_results(strategy_id)
    return {"strategy_id": strategy_id, "results": results}

@router.get("/results/detailed/{result_id}")
def get_detailed_backtest_result(result_id: int, db: Session = Depends(get_db)):
    """Get detailed backtest result including equity curve and trades"""
    
    from ...database.models import BacktestResult
    
    result = db.query(BacktestResult).filter(BacktestResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Backtest result not found")
    
    return {
        "id": result.id,
        "strategy_id": result.strategy_id,
        "start_date": result.start_date.isoformat(),
        "end_date": result.end_date.isoformat(),
        "initial_capital": result.initial_capital,
        "final_capital": result.final_capital,
        "total_return": result.total_return,
        "total_trades": result.total_trades,
        "winning_trades": result.winning_trades,
        "losing_trades": result.losing_trades,
        "win_rate": result.win_rate,
        "profit_factor": result.profit_factor,
        "sharpe_ratio": result.sharpe_ratio,
        "max_drawdown": result.max_drawdown,
        "avg_trade_duration": result.avg_trade_duration,
        "equity_curve": result.equity_curve,
        "trade_history": result.trade_history,
        "monthly_returns": result.monthly_returns,
        "created_at": result.created_at.isoformat()
    }

@router.get("/performance/comparison")
async def compare_strategies(strategy_ids: str, db: Session = Depends(get_db)):
    """Compare performance of multiple strategies"""
    
    try:
        ids = [int(id.strip()) for id in strategy_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid strategy IDs format")
    
    comparison_data = []
    
    for strategy_id in ids:
        results = await backtesting_engine.get_backtest_results(strategy_id)
        
        if results:
            # Get the most recent backtest result
            latest_result = results[0]
            
            comparison_data.append({
                "strategy_id": strategy_id,
                "total_return": latest_result.get('total_return', 0),
                "win_rate": latest_result.get('win_rate', 0),
                "sharpe_ratio": latest_result.get('sharpe_ratio', 0),
                "max_drawdown": latest_result.get('max_drawdown', 0),
                "total_trades": latest_result.get('total_trades', 0)
            })
    
    return {"comparison": comparison_data}

@router.post("/optimize")
async def optimize_strategy_parameters(
    strategy_id: int,
    parameter_ranges: dict,
    optimization_metric: str = 'sharpe_ratio',
    db: Session = Depends(get_db)
):
    """Optimize strategy parameters using grid search"""
    
    # This is a placeholder for parameter optimization
    # In a full implementation, you would:
    # 1. Generate parameter combinations
    # 2. Run backtests for each combination
    # 3. Find the best performing parameters
    
    return {
        "message": "Parameter optimization not yet implemented",
        "strategy_id": strategy_id,
        "parameter_ranges": parameter_ranges,
        "optimization_metric": optimization_metric
    }

@router.get("/monte-carlo/{strategy_id}")
async def monte_carlo_analysis(
    strategy_id: int,
    simulations: int = 1000,
    confidence_interval: float = 0.95
):
    """Run Monte Carlo analysis on backtest results"""
    
    # This is a placeholder for Monte Carlo analysis
    # In a full implementation, you would:
    # 1. Get historical trade returns
    # 2. Run Monte Carlo simulations
    # 3. Calculate confidence intervals
    # 4. Return risk metrics
    
    return {
        "message": "Monte Carlo analysis not yet implemented",
        "strategy_id": strategy_id,
        "simulations": simulations,
        "confidence_interval": confidence_interval
    }