# ibkr_streaming/ws_push.py

import asyncio
import json
import math
import websockets
import os
from urllib.parse import urlparse, parse_qs
from .config import NODE_GATEWAY_WS_URL
from ai_core.core.logger import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------
# JSON Sanitization Helper
# ------------------------------------------------------------
def sanitize_for_json(obj):
    """Recursively sanitize data to remove NaN and Infinity values."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None  # Convert NaN/Infinity to null
        return obj
    return obj

# ------------------------------------------------------------
# Global handler for incoming messages
# ------------------------------------------------------------
_command_handler = None

# Connection state
_ws_connection = None
_connection_attempts = 0
_connection_task = None
_connection_task_started = False
_connection_lock = asyncio.Lock()

def register_command_handler(handler):
    """Register a callback function to handle incoming WebSocket messages."""
    global _command_handler
    _command_handler = handler
    logger.info("✅ WebSocket command handler registered")

# ------------------------------------------------------------
# BACKGROUND TASK — keep WS connected forever & READ messages
# ------------------------------------------------------------
async def _maintain_connection():
    """Keeps WebSocket connection alive, reconnects on failure, and reads messages."""
    global _ws_connection, _connection_attempts

    # Allow Node gateway to boot
    await asyncio.sleep(1)

    while True:
        try:
            # If connection exists but is CLOSED → reset it
            if _ws_connection is not None:
                if _ws_connection.closed:
                    _ws_connection = None

            # If we have no connection → create one
            if _ws_connection is None:
                _connection_attempts += 1

                try:
                    conn = await websockets.connect(
                        NODE_GATEWAY_WS_URL,
                        ping_interval=20,
                        ping_timeout=10
                    )
                    _ws_connection = conn
                    _connection_attempts = 0
                    logger.info(f"✅ WebSocket connected to Node Gateway at {NODE_GATEWAY_WS_URL}")
                    
                    # Connection successful - start reading loop
                    try:
                        async for message in conn:
                            # Handle incoming message
                            if _command_handler:
                                try:
                                    data = json.loads(message)
                                    await _command_handler(data)
                                except json.JSONDecodeError:
                                    logger.warning(f"Received invalid JSON: {message}")
                                except Exception as e:
                                    logger.error(f"Error handling message: {e}")
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed")
                    
                    # If loop exits, connection is closed
                    _ws_connection = None

                except Exception as e:
                    if _connection_attempts == 1 or _connection_attempts % 10 == 0:
                        logger.warning(f"WebSocket connect attempt #{_connection_attempts} failed: {e}")
                    await asyncio.sleep(2)
                    continue

            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"WebSocket error in connection maintenance: {e}")
            _ws_connection = None
            await asyncio.sleep(2)



# ------------------------------------------------------------
# RETURN ACTIVE CONNECTION (or None)
# ------------------------------------------------------------
async def _get_connection():
    global _ws_connection, _connection_task_started, _connection_task

    # Start background task once
    if not _connection_task_started:
        async with _connection_lock:
            if not _connection_task_started:
                logger.info("Starting WebSocket connection maintenance task...")
                _connection_task = asyncio.create_task(_maintain_connection())
                _connection_task_started = True
                await asyncio.sleep(0.5)

    # Wait for connection to initialize
    waited = 0
    while _ws_connection is None and waited < 10:
        await asyncio.sleep(0.2)
        waited += 0.2

    if _ws_connection is None:
        logger.debug("WS connection unavailable after wait")
        return None

    # Check connection status
    try:
        if not _ws_connection.closed:
            return _ws_connection
        logger.debug("WS connection is closed")
    except Exception as e:
        logger.debug(f"WS check failed: {e}")

    _ws_connection = None
    return None


# ------------------------------------------------------------
# PUSH DATA TO NODE GATEWAY
# ------------------------------------------------------------
async def push(data):
    global _ws_connection

    try:
        conn = await _get_connection()
        if conn is None:
            logger.debug("Skipping push: No active WS connection.")
            return

        # Send JSON - sanitize to avoid NaN/Infinity errors
        try:
            sanitized_data = sanitize_for_json(data)
            await conn.send(json.dumps(sanitized_data, allow_nan=False))
            # Safe symbol extraction for logging
            symbol = None
            if isinstance(data, dict):
                symbol = data.get("symbol") or data.get("data", {}).get("symbol") if isinstance(data.get("data"), dict) else None
            logger.debug(f"[PUSH] Sent data for {symbol or 'unknown'}")

        except (websockets.exceptions.ConnectionClosed, OSError) as e:
            logger.warning(f"WS closed during send: {e}")
            try:
                await conn.close()
            except:
                pass
            _ws_connection = None  # reconnect
        except Exception as e:
            logger.error(f"Send error: {e}")

    except Exception as e:
        logger.error(f"Fatal push error: {e}", exc_info=True)
        _ws_connection = None
