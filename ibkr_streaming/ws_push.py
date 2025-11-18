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
_connection_lock = asyncio.Lock()  # Lock to prevent concurrent connection attempts
_connection_task = None  # Background task to maintain connection
_connection_task_started = False  # Track if task has been started

async def _maintain_connection():
    """Background task to maintain WebSocket connection and handle reconnection"""
    global _ws_connection, _connection_attempts
    
    # Wait a bit for Node Gateway to be ready (if Python starts first)
    await asyncio.sleep(1)
    
    while True:
        try:
            # Close old connection if it exists but is not open
            if _ws_connection is not None:
                try:
                    if not _ws_connection.open:
                        try:
                            await _ws_connection.close()
                        except:
                            pass
                        _ws_connection = None
                except (AttributeError, Exception):
                    # Connection is invalid, close it
                    try:
                        await _ws_connection.close()
                    except:
                        pass
                    _ws_connection = None
            
            # Only create new connection if we don't have one
            if _ws_connection is None:
                # Try to reconnect
                _connection_attempts += 1
                try:
                    # IMPORTANT: Use async with to ensure proper cleanup
                    # But we can't use async with in a loop, so we'll manage it manually
                    conn = await websockets.connect(
                        NODE_GATEWAY_WS_URL,
                        ping_interval=20,
                        ping_timeout=10
                    )
                    # Only set if we successfully created it
                    _ws_connection = conn
                    logger.info(f"✅ WebSocket connected to Node Gateway at {NODE_GATEWAY_WS_URL}")
                    _connection_attempts = 0  # Reset on success
                except Exception as e:
                    # Only log connection failures every 10 attempts to reduce spam
                    if _connection_attempts == 1 or _connection_attempts % 10 == 0:
                        logger.warning(f"Connection attempt {_connection_attempts} failed: {e}")
                        if _connection_attempts == 1:
                            logger.info("💡 Make sure Node Gateway is running: cd node_gateway && npm start")
                    await asyncio.sleep(2)  # Wait before retry
                    continue
            
            # Wait a bit before checking again
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in connection maintenance: {e}")
            # Close connection on error
            if _ws_connection is not None:
                try:
                    await _ws_connection.close()
                except:
                    pass
            _ws_connection = None
            await asyncio.sleep(2)

async def _get_connection():
    """Get or create WebSocket connection. Thread-safe."""
    global _ws_connection, _connection_task, _connection_task_started
    
    # Start background task ONLY ONCE (outside lock to avoid blocking)
    if not _connection_task_started:
        async with _connection_lock:
            # Double-check inside lock (prevent race condition)
            if not _connection_task_started:
                logger.info("Starting WebSocket connection maintenance task...")
                _connection_task = asyncio.create_task(_maintain_connection())
                _connection_task_started = True
                # Give it a moment to start
                await asyncio.sleep(0.5)
    
    # Wait for connection to be established (with timeout)
    max_wait = 10
    waited = 0
    while _ws_connection is None and waited < max_wait:
        await asyncio.sleep(0.2)
        waited += 0.2
    
    if _ws_connection is None:
        logger.debug(f"Connection not available after {max_wait}s wait")
        return None
    
    # Verify connection is open
    try:
        if _ws_connection.open:
            return _ws_connection
        else:
            logger.debug("Connection exists but is not open")
            _ws_connection = None
            return None
    except (AttributeError, Exception) as e:
        logger.debug(f"Error checking connection: {e}")
        _ws_connection = None
        return None

async def push(data):
    """Push data to WebSocket gateway"""
    global _ws_connection
    
    try:
        # Get connection (will wait for it to be ready)
        conn = await _get_connection()
        if conn is None:
            logger.debug("WebSocket connection not available, skipping message")
            return
        
        # Send data
        try:
            await conn.send(json.dumps(data))
            try:
                symbol = data.get('symbol') or data.get('data', {}).get('symbol') or 'unknown'
                logger.debug(f"Data pushed to WebSocket: {symbol}")
            except Exception:
                logger.debug("Data pushed to WebSocket")
                
        except (websockets.exceptions.ConnectionClosed, AttributeError, OSError) as e:
            logger.warning(f"WebSocket connection closed during send: {e}")
            # Close the connection properly
            if _ws_connection is not None:
                try:
                    await _ws_connection.close()
                except:
                    pass
            _ws_connection = None
            # Background task will reconnect
        
    except Exception as e:
        logger.error(f"WebSocket error in push: {e}", exc_info=True)
        _ws_connection = None
