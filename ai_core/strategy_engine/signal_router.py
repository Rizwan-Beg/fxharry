# ai_core/strategy_engine/signal_router.py

from typing import Optional
from ai_core.core.logger import get_logger

logger = get_logger(__name__)


class SignalRouter:
    def __init__(self, ws_broadcaster, execution_engine=None):
        """
        Initialize signal router.
        
        Args:
            ws_broadcaster: WebSocket broadcaster for UI
            execution_engine: ExecutionEngine instance (optional)
        """
        self.ws_broadcaster = ws_broadcaster
        self.execution_engine = execution_engine
        self.execution_enabled = execution_engine is not None
        
        logger.info(f"SignalRouter initialized (execution_enabled={self.execution_enabled})")

    async def broadcast_signals(self, signals):
        """
        Route signals to both UI and execution engine.
        
        Args:
            signals: List of trading signals
        """
        if not signals:
            return

        # Broadcast to UI via WebSocket
        payload = {
            "type": "signal_update",
            "data": signals
        }
        await self.ws_broadcaster(payload)
        
        # Route to execution engine if enabled
        if self.execution_enabled and self.execution_engine:
            try:
                logger.info(f"Routing {len(signals)} signals to execution engine")
                await self.execution_engine.process_signals(signals)
            except Exception as e:
                logger.error(f"Error routing signals to execution engine: {e}", exc_info=True)

