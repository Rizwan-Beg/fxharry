# ibkr_streaming/ibkr_client.py

from ib_async import IB
from .config import IBKR_HOST, IBKR_PORT, IBKR_CLIENT_ID
from .logger import get_logger

logger = get_logger(__name__)

ib = IB()

def connect_ibkr():
    """Connect to IBKR synchronously (nest_asyncio allows this in async context)"""
    logger.info("=" * 80)
    logger.info("IBKR Connection Initialization")
    logger.info(f"Host: {IBKR_HOST}, Port: {IBKR_PORT}, Client ID: {IBKR_CLIENT_ID}")
    
    if not ib.isConnected():
        logger.info("🔌 Initiating connection to IBKR TWS/Gateway...")
        try:
            ib.connect(IBKR_HOST, IBKR_PORT, clientId=IBKR_CLIENT_ID)
            logger.info("✅ Successfully connected to IBKR")
            logger.info(f"Connection Status: {ib.isConnected()}")
            logger.info(f"Client ID: {IBKR_CLIENT_ID}")
            try:
                ib.reqMarketDataType(1)
                logger.info("Market data type set to REALTIME (1)")
            except Exception:
                logger.warning("Unable to set market data type; continuing with default")
        except Exception as e:
            logger.error(f"❌ Failed to connect to IBKR: {e}", exc_info=True)
            raise
    else:
        logger.info("ℹ️  Already connected to IBKR (reusing existing connection)")
        logger.info(f"Connection Status: {ib.isConnected()}")
    
    logger.info("=" * 80)
    return ib
