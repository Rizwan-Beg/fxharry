import asyncio
import json
import math
import websockets
import os
from .config import NODE_GATEWAY_WS_URL
from ai_core.core.logger import get_logger

logger = get_logger(__name__)

# websockets v15 uses .state (int): 1=OPEN, 2=CLOSING, 3=CLOSED
_WS_STATE_OPEN = 1

def _is_open(conn) -> bool:
    """Return True if a websockets v15 connection is in the OPEN state."""
    try:
        return conn is not None and conn.state == _WS_STATE_OPEN
    except Exception:
        return False

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

# Connection state — _ws_connection is set as soon as connect() succeeds,
# BEFORE entering the read loop, so push() can use it immediately.
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
            # Reset stale connection
            if _ws_connection is not None and not _is_open(_ws_connection):
                _ws_connection = None

            if _ws_connection is None:
                _connection_attempts += 1
                try:
                    conn = await websockets.connect(
                        NODE_GATEWAY_WS_URL,
                        ping_interval=20,
                        ping_timeout=10,
                        open_timeout=5,
                    )
                    # *** KEY FIX: set global BEFORE entering read loop ***
                    _ws_connection = conn
                    _connection_attempts = 0
                    logger.info(f"✅ WebSocket connected to Node Gateway at {NODE_GATEWAY_WS_URL}")

                    # Read loop — runs while connection is alive
                    try:
                        async for message in conn:
                            if _command_handler:
                                try:
                                    data = json.loads(message)
                                    # Skip welcome message silently
                                    if data.get("type") == "welcome":
                                        continue
                                    await _command_handler(data)
                                except json.JSONDecodeError:
                                    logger.warning(f"Received invalid JSON: {message}")
                                except Exception as e:
                                    logger.error(f"Error handling message: {e}")
                    except websockets.exceptions.ConnectionClosed as e:
                        logger.warning(f"WebSocket connection closed: {e}")
                    except Exception as e:
                        logger.error(f"Read loop error: {e}")
                    finally:
                        # Connection died — clear it so we reconnect next iteration
                        _ws_connection = None
                        logger.info("WebSocket connection lost, will reconnect...")

                except Exception as e:
                    if _connection_attempts == 1 or _connection_attempts % 10 == 0:
                        logger.warning(
                            f"WebSocket connect attempt #{_connection_attempts} failed: {e}"
                        )
                    _ws_connection = None
                    await asyncio.sleep(2)
                    continue

            # Already connected — just sleep and check again
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"WebSocket error in connection maintenance: {e}")
            _ws_connection = None
            await asyncio.sleep(2)


# ------------------------------------------------------------
# START CONNECTION TASK (call once from run.py at startup)
# ------------------------------------------------------------
async def start_connection():
    """Explicitly start the WebSocket connection maintenance task.
    Call this once at startup BEFORE the first push()."""
    global _connection_task, _connection_task_started
    async with _connection_lock:
        if not _connection_task_started:
            logger.info("Starting WebSocket connection maintenance task...")
            _connection_task = asyncio.create_task(_maintain_connection())
            _connection_task_started = True
            # Wait up to 3 seconds for initial connection
            for _ in range(15):
                await asyncio.sleep(0.2)
                if _ws_connection is not None and _is_open(_ws_connection):
                    logger.info("✅ WebSocket ready for push")
                    return
            logger.warning("⚠️ WebSocket not yet connected after 3s, will retry in background")


# ------------------------------------------------------------
# RETURN ACTIVE CONNECTION (or None)
# ------------------------------------------------------------
async def _get_connection():
    global _connection_task_started, _connection_task

    # Start background task lazily if not started
    if not _connection_task_started:
        async with _connection_lock:
            if not _connection_task_started:
                logger.info("Starting WebSocket connection maintenance task (lazy)...")
                _connection_task = asyncio.create_task(_maintain_connection())
                _connection_task_started = True

    # Wait up to 3 seconds for connection
    for _ in range(15):
        if _ws_connection is not None:
            try:
                if _is_open(_ws_connection):
                    return _ws_connection
            except Exception:
                pass
        await asyncio.sleep(0.2)

    logger.debug("WS connection unavailable after wait")
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

        try:
            sanitized_data = sanitize_for_json(data)
            await conn.send(json.dumps(sanitized_data, allow_nan=False))

            # Safe symbol extraction for debug logging
            symbol = None
            if isinstance(data, dict):
                symbol = data.get("symbol")
                if not symbol and isinstance(data.get("data"), dict):
                    symbol = data["data"].get("symbol")
            logger.debug(f"[PUSH] Sent {data.get('type', 'unknown')} for {symbol or 'unknown'}")

        except (websockets.exceptions.ConnectionClosed, OSError) as e:
            logger.warning(f"WS closed during send: {e}")
            try:
                await conn.close()
            except Exception:
                pass
            _ws_connection = None  # triggers reconnect
        except Exception as e:
            logger.error(f"Send error: {e}")

    except Exception as e:
        logger.error(f"Fatal push error: {e}", exc_info=True)
        _ws_connection = None
