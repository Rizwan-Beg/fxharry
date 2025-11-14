# ibkr_streaming/ws_push.py

import asyncio
import json
import websockets
from .config import NODE_GATEWAY_WS_URL
from .logger import get_logger

logger = get_logger(__name__)

# Cache for WebSocket connection
_ws_connection = None
_connection_attempts = 0
_last_error_ts = 0

async def push(data):
    """Push data to WebSocket gateway"""
    global _ws_connection, _connection_attempts
    
    try:
        if _ws_connection is None or _ws_connection.closed:
            logger.debug(f"Establishing WebSocket connection to {NODE_GATEWAY_WS_URL}")
            _connection_attempts += 1
            try:
                _ws_connection = await websockets.connect(
                    NODE_GATEWAY_WS_URL,
                    ping_interval=20,
                    ping_timeout=10
                )
                logger.info(f"✅ WebSocket connected to {NODE_GATEWAY_WS_URL}")
                _connection_attempts = 0
            except Exception as e:
                logger.warning(f"WebSocket connection attempt {_connection_attempts} failed: {e}")
                return

        await _ws_connection.send(json.dumps(data))
        try:
            symbol = data.get('symbol') or data.get('data', {}).get('symbol') or 'unknown'
            logger.debug(f"Data pushed to WebSocket: {symbol}")
        except Exception:
            logger.debug("Data pushed to WebSocket")
        
    except websockets.exceptions.ConnectionClosed:
        logger.warning("WebSocket connection closed. Will attempt to reconnect on next push.")
        _ws_connection = None
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        _ws_connection = None
