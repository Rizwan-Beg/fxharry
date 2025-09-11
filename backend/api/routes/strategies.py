from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Strategy
from services.strategy_manager import StrategyManager
from pydantic import BaseModel
import os
import shutil

router = APIRouter()
strategy_manager = StrategyManager()

class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str  # 'python', 'cpp', 'ml_model'
    parameters: Optional[dict] = None

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict] = None
    is_active: Optional[bool] = None

@router.post("/", response_model=dict)
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new trading strategy"""
    
    # Check if strategy name already exists
    existing = db.query(Strategy).filter(Strategy.name == strategy.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Strategy name already exists")
    
    db_strategy = Strategy(
        name=strategy.name,
        description=strategy.description,
        strategy_type=strategy.strategy_type,
        parameters=strategy.parameters
    )
    
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    
    return {
        "id": db_strategy.id,
        "name": db_strategy.name,
        "message": "Strategy created successfully"
    }

@router.post("/{strategy_id}/upload")
async def upload_strategy_file(
    strategy_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload strategy file (Python script, C++ binary, or ML model)"""
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Create strategies directory if it doesn't exist
    strategies_dir = "strategies"
    os.makedirs(strategies_dir, exist_ok=True)
    
    # Save uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"strategy_{strategy_id}{file_extension}"
    file_path = os.path.join(strategies_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update strategy with file path
    strategy.file_path = file_path
    db.commit()
    
    return {"message": "Strategy file uploaded successfully", "file_path": file_path}

@router.get("/", response_model=List[dict])
def get_strategies(db: Session = Depends(get_db)):
    """Get all trading strategies"""
    strategies = db.query(Strategy).all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "strategy_type": s.strategy_type,
            "is_active": s.is_active,
            "total_trades": s.total_trades,
            "winning_trades": s.winning_trades,
            "total_pnl": s.total_pnl,
            "sharpe_ratio": s.sharpe_ratio,
            "max_drawdown": s.max_drawdown,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        }
        for s in strategies
    ]

@router.get("/{strategy_id}", response_model=dict)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get specific strategy details"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "strategy_type": strategy.strategy_type,
        "parameters": strategy.parameters,
        "is_active": strategy.is_active,
        "file_path": strategy.file_path,
        "total_trades": strategy.total_trades,
        "winning_trades": strategy.winning_trades,
        "total_pnl": strategy.total_pnl,
        "sharpe_ratio": strategy.sharpe_ratio,
        "max_drawdown": strategy.max_drawdown,
        "created_at": strategy.created_at.isoformat(),
        "updated_at": strategy.updated_at.isoformat()
    }

@router.put("/{strategy_id}", response_model=dict)
def update_strategy(strategy_id: int, strategy_update: StrategyUpdate, db: Session = Depends(get_db)):
    """Update strategy details"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy_update.name is not None:
        # Check if new name conflicts with existing strategies
        existing = db.query(Strategy).filter(
            Strategy.name == strategy_update.name,
            Strategy.id != strategy_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Strategy name already exists")
        strategy.name = strategy_update.name
    
    if strategy_update.description is not None:
        strategy.description = strategy_update.description
    
    if strategy_update.parameters is not None:
        strategy.parameters = strategy_update.parameters
    
    if strategy_update.is_active is not None:
        strategy.is_active = strategy_update.is_active
    
    db.commit()
    
    return {"message": "Strategy updated successfully"}

@router.post("/{strategy_id}/activate")
async def activate_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Activate a trading strategy"""
    success = await strategy_manager.activate_strategy(strategy_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {"message": "Strategy activated successfully"}

@router.post("/{strategy_id}/deactivate")
async def deactivate_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Deactivate a trading strategy"""
    success = await strategy_manager.deactivate_strategy(strategy_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {"message": "Strategy deactivated successfully"}

@router.delete("/{strategy_id}")
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Delete a trading strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Remove strategy file if it exists
    if strategy.file_path and os.path.exists(strategy.file_path):
        os.remove(strategy.file_path)
    
    db.delete(strategy)
    db.commit()
    
    return {"message": "Strategy deleted successfully"}

@router.get("/{strategy_id}/performance")
def get_strategy_performance(strategy_id: int, db: Session = Depends(get_db)):
    """Get strategy performance metrics"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Get recent trades for this strategy
    recent_trades = db.query(Strategy).filter(
        Strategy.id == strategy_id
    ).first().trades[-10:]  # Last 10 trades
    
    return {
        "strategy_id": strategy_id,
        "total_trades": strategy.total_trades,
        "winning_trades": strategy.winning_trades,
        "losing_trades": strategy.total_trades - strategy.winning_trades,
        "win_rate": strategy.winning_trades / strategy.total_trades if strategy.total_trades > 0 else 0,
        "total_pnl": strategy.total_pnl,
        "sharpe_ratio": strategy.sharpe_ratio,
        "max_drawdown": strategy.max_drawdown,
        "recent_trades": [
            {
                "id": trade.id,
                "symbol": trade.symbol,
                "action": trade.action,
                "pnl": trade.pnl,
                "entry_time": trade.entry_time.isoformat(),
                "status": trade.status
            }
            for trade in recent_trades
        ]
    }