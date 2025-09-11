from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import uvicorn

from database.database import get_db, engine, Base
from database.models import Strategy, Trade, BacktestResult
from services.strategy_manager import StrategyManager
from services.ibkr_service import IBKRService
from services.market_data_service import MarketDataService
from services.risk_manager import RiskManager
from services.backtesting_engine import BacktestingEngine
from api.routes import strategies, trades, backtesting, account
from websocket.connection_manager import ConnectionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Forex Trading Dashboard", version="1.0.0")

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
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize IBKR connection
    await ibkr_service.initialize()
    
    # Start market data streaming
    asyncio.create_task(stream_market_data())
    
    logger.info("Trading dashboard started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await ibkr_service.disconnect()
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)