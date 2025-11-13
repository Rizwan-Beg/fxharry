import asyncio
import json
from datetime import datetime
import contextlib
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .core.config import settings
from .core.logger import get_logger, shutdown_logging
from .database.database import engine
from .database.models import Base
from ai_core.strategy_engine.rule_based import StrategyManager
from ai_core.strategy_engine.broker.ibkr_service import IBKRService
from ai_core.strategy_engine.market_data.market_data_service import MarketDataService
from ai_core.risk_manager.risk_manager import RiskManager
from ai_core.backtesting.engine import BacktestingEngine
from ai_core.api.routes import strategies, trades, backtesting, account
from ai_core.api.websocket.connection_manager import ConnectionManager

logger = get_logger(__name__)
market_data_task: Optional[asyncio.Task] = None

app = FastAPI(title=settings.app_name, version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
strategy_manager = StrategyManager()
ibkr_service = IBKRService()
market_data_service = MarketDataService()
risk_manager = RiskManager()
backtesting_engine = BacktestingEngine()
connection_manager = ConnectionManager()

# Include API routes
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(backtesting.router, prefix="/api/backtesting", tags=["backtesting"])
app.include_router(account.router, prefix="/api/account", tags=["account"])

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    global market_data_task

    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize IBKR connection
    try:
        await ibkr_service.connect()
    except Exception as exc:
        logger.error("Failed to establish broker connection: %s", exc)
    
    # Start market data streaming
    market_data_task = asyncio.create_task(stream_market_data())
    
    logger.info("Trading dashboard started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global market_data_task

    if market_data_task:
        market_data_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await market_data_task
        market_data_task = None

    await ibkr_service.disconnect()
    shutdown_logging()
    logger.info("Trading dashboard shut down")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

async def stream_market_data():
    """Stream live market data and AI signals"""
    while True:
        try:
            # Get live forex data
            forex_data = await market_data_service.get_live_forex_data(['EURUSD', 'GBPUSD', 'XAUUSD'])
            
            # Process through active strategies
            active_strategies = strategy_manager.get_active_strategies()
            signals = []
            
            for strategy in active_strategies:
                signal = await strategy_manager.process_strategy(strategy.id, forex_data)
                if signal:
                    signals.append(signal)
            
            # Broadcast data to connected clients
            market_update = {
                'type': 'market_data',
                'data': forex_data,
                'signals': signals,
                'timestamp': datetime.now().isoformat()
            }
            
            await connection_manager.broadcast(json.dumps(market_update))
            
            # Risk assessment
            risk_assessment = risk_manager.assess_portfolio_risk()
            if risk_assessment['risk_level'] > 0.7:  # High risk threshold
                risk_alert = {
                    'type': 'risk_alert',
                    'data': risk_assessment,
                    'timestamp': datetime.now().isoformat()
                }
                await connection_manager.broadcast(json.dumps(risk_alert))
            
        except Exception as e:
            logger.error(f"Error in market data stream: {e}")
        
        await asyncio.sleep(1)  # 1 second intervals

@app.get("/")
async def root():
    return {"message": "AI Forex Trading Dashboard API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "ibkr": "connected" if ibkr_service.is_connected() else "disconnected",
            "market_data": "streaming"
        }
    }

if __name__ == "__main__":
    uvicorn.run("ai_core.main:app", host="127.0.0.1", port=8000, reload=True)