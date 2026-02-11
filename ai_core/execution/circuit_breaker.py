"""Circuit breaker for automatic trading halt under adverse conditions."""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from ai_core.core.logger import get_logger
from . import execution_config

logger = get_logger(__name__)


class CircuitBreaker:
    """
    Automatic safety mechanism to halt trading under adverse conditions.
    
    Trigger conditions:
    - Daily loss exceeds threshold
    - Consecutive losing trades exceed limit
    - Manual emergency stop
    
    The circuit breaker can be reset manually or automatically at the start
    of a new trading day.
    """
    
    def __init__(self):
        self.is_tripped = False
        self.trip_reason = None
        self.trip_time = None
        self.consecutive_losses = 0
        self.daily_start_equity = None
        self.last_reset_date = None
        self._manual_stop = False
        
        logger.info("Circuit breaker initialized")
    
    def check_and_update(
        self,
        daily_pnl: float,
        account_equity: float,
        last_trade_profitable: Optional[bool] = None
    ) -> bool:
        """
        Check circuit breaker conditions and update state.
        
        Args:
            daily_pnl: Today's total PnL
            account_equity: Current account equity
            last_trade_profitable: Whether the last trade was profitable
            
        Returns:
            True if circuit breaker is tripped, False otherwise
        """
        if not execution_config.ENABLE_CIRCUIT_BREAKER:
            return False
        
        # Auto-reset at start of new trading day
        self._check_daily_reset()
        
        # Check if already tripped
        if self.is_tripped:
            return True
        
        # Set daily start equity if not set
        if self.daily_start_equity is None:
            self.daily_start_equity = account_equity - daily_pnl
        
        # Check daily loss threshold
        if self.daily_start_equity > 0:
            daily_loss_percent = daily_pnl / self.daily_start_equity
            
            if daily_loss_percent <= execution_config.CIRCUIT_BREAKER_LOSS_THRESHOLD:
                self._trip(
                    f"Daily loss threshold exceeded: "
                    f"{daily_loss_percent:.2%} <= {execution_config.CIRCUIT_BREAKER_LOSS_THRESHOLD:.2%}"
                )
                return True
        
        # Check consecutive losses
        if last_trade_profitable is not None:
            if last_trade_profitable:
                self.consecutive_losses = 0
            else:
                self.consecutive_losses += 1
                
                if self.consecutive_losses >= execution_config.CIRCUIT_BREAKER_CONSECUTIVE_LOSSES:
                    self._trip(
                        f"Consecutive losing trades exceeded: "
                        f"{self.consecutive_losses} >= {execution_config.CIRCUIT_BREAKER_CONSECUTIVE_LOSSES}"
                    )
                    return True
        
        # Check manual stop
        if self._manual_stop:
            if not self.is_tripped:
                self._trip("Manual emergency stop activated")
            return True
        
        return False
    
    def _trip(self, reason: str):
        """Trip the circuit breaker."""
        self.is_tripped = True
        self.trip_reason = reason
        self.trip_time = datetime.now()
        
        logger.critical("=" * 80)
        logger.critical("🚨 CIRCUIT BREAKER TRIPPED 🚨")
        logger.critical(f"Reason: {reason}")
        logger.critical(f"Time: {self.trip_time.isoformat()}")
        logger.critical("All trading has been halted.")
        logger.critical("=" * 80)
    
    def manual_trip(self, reason: str = "Manual activation"):
        """Manually trip the circuit breaker (kill switch)."""
        self._manual_stop = True
        self._trip(reason)
    
    def reset(self, force: bool = False) -> bool:
        """
        Reset the circuit breaker.
        
        Args:
            force: If True, reset regardless of conditions
            
        Returns:
            True if reset successful, False otherwise
        """
        if not force and self.is_tripped:
            # Don't allow reset if tripped less than 1 hour ago (safety measure)
            if self.trip_time:
                time_since_trip = datetime.now() - self.trip_time
                if time_since_trip < timedelta(hours=1):
                    logger.warning(
                        f"Circuit breaker reset denied - tripped only "
                        f"{time_since_trip.total_seconds() / 60:.1f} minutes ago"
                    )
                    return False
        
        logger.info("Circuit breaker reset")
        self.is_tripped = False
        self.trip_reason = None
        self.trip_time = None
        self.consecutive_losses = 0
        self._manual_stop = False
        
        return True
    
    def _check_daily_reset(self):
        """Check if we should auto-reset at start of new trading day."""
        today = datetime.now().date()
        
        if self.last_reset_date != today:
            logger.info(f"New trading day detected: {today}")
            self.last_reset_date = today
            self.daily_start_equity = None
            self.consecutive_losses = 0
            
            # Auto-reset if it was tripped yesterday
            if self.is_tripped and self.trip_time:
                if self.trip_time.date() < today:
                    logger.info("Auto-resetting circuit breaker for new trading day")
                    self.reset(force=True)
    
    def get_status(self) -> Dict:
        """Get current circuit breaker status."""
        return {
            "enabled": execution_config.ENABLE_CIRCUIT_BREAKER,
            "is_tripped": self.is_tripped,
            "trip_reason": self.trip_reason,
            "trip_time": self.trip_time.isoformat() if self.trip_time else None,
            "consecutive_losses": self.consecutive_losses,
            "consecutive_loss_limit": execution_config.CIRCUIT_BREAKER_CONSECUTIVE_LOSSES,
            "daily_loss_threshold": execution_config.CIRCUIT_BREAKER_LOSS_THRESHOLD,
        }
