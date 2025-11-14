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
        # Check if connection exists and is open
        # websockets library uses 'open' property, not 'closed'
        connection_is_open = False
        if _ws_connection is not None:
            try:
                # Check if connection is open by accessing the 'open' property
                connection_is_open = _ws_connection.open
            except (AttributeError, Exception):
                # If 'open' doesn't exist or connection is broken, treat as closed
                connection_is_open = False
        
        if _ws_connection is None or not connection_is_open:
            logger.debug(f"Establishing WebSocket connection to {NODE_GATEWAY_WS_URL}")
            _connection_attempts += 1
            try:
                _ws_connection = await websockets.connect(
                    NODE_GATEWAY_WS_URL,
                    ping_interval=20,
                    ping_timeout=10
                )
                logger.info(f"✅ WebSocket connected to Node Gateway at {NODE_GATEWAY_WS_URL}")
                _connection_attempts = 0
            except Exception as e:
                if _connection_attempts <= 3 or _connection_attempts % 10 == 0:
                    logger.warning(f"WebSocket connection attempt {_connection_attempts} failed: {e}")
                _ws_connection = None
                return

        # Send data if connection is open
        if _ws_connection is not None:
            try:
                await _ws_connection.send(json.dumps(data))
                try:
                    symbol = data.get('symbol') or data.get('data', {}).get('symbol') or 'unknown'
                    logger.debug(f"Data pushed to WebSocket: {symbol}")
                except Exception:
                    logger.debug("Data pushed to WebSocket")
            except (websockets.exceptions.ConnectionClosed, AttributeError) as e:
                logger.warning(f"WebSocket connection closed during send: {e}")
                _ws_connection = None
                # Try to reconnect immediately
                try:
                    _ws_connection = await websockets.connect(
                        NODE_GATEWAY_WS_URL,
                        ping_interval=20,
                        ping_timeout=10
                    )
                    logger.info(f"✅ WebSocket reconnected to Node Gateway")
                    # Retry sending
                    await _ws_connection.send(json.dumps(data))
                except Exception as retry_e:
                    logger.warning(f"Failed to reconnect: {retry_e}")
                    _ws_connection = None
        
    except websockets.exceptions.ConnectionClosed:
        logger.warning("WebSocket connection closed. Will attempt to reconnect on next push.")
        _ws_connection = None
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        _ws_connection = None
