"""Position tracking and P&L management."""

from typing import Dict, Optional, Any
from datetime import datetime
from ai_core.core.logger import get_logger

logger = get_logger(__name__)


class Position:
    """Represents an open trading position."""
    
    def __init__(
        self,
        symbol: str,
        action: str,
        quantity: float,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trade_id: Optional[int] = None,
    ):
        self.symbol = symbol
        self.action = action.upper()  # BUY (LONG) or SELL (SHORT)
        self.quantity = quantity
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.trade_id = trade_id
        
        self.current_price = entry_price
        self.entry_time = datetime.now()
        self.unrealized_pnl = 0.0
        
        logger.info(
            f"Position opened: {action} {quantity} {symbol} @ {entry_price} "
            f"(SL: {stop_loss}, TP: {take_profit})"
        )
    
    def update_price(self, current_price: float):
        """Update current price and recalculate P&L."""
        self.current_price = current_price
        self.unrealized_pnl = self._calculate_pnl()
    
    def _calculate_pnl(self) -> float:
        """Calculate unrealized P&L."""
        if self.action == "BUY":
            # Long position: profit when price goes up
            pnl = (self.current_price - self.entry_price) * self.quantity
        else:  # SELL
            # Short position: profit when price goes down
            pnl = (self.entry_price - self.current_price) * self.quantity
        
        return pnl
    
    def check_stop_loss_hit(self) -> bool:
        """Check if stop loss has been hit."""
        if self.stop_loss is None:
            return False
        
        if self.action == "BUY":
            return self.current_price <= self.stop_loss
        else:  # SELL
            return self.current_price >= self.stop_loss
    
    def check_take_profit_hit(self) -> bool:
        """Check if take profit has been hit."""
        if self.take_profit is None:
            return False
        
        if self.action == "BUY":
            return self.current_price >= self.take_profit
        else:  # SELL
            return self.current_price <= self.take_profit
    
    def get_pnl_percent(self) -> float:
        """Get P&L as percentage of position value."""
        position_value = self.entry_price * self.quantity
        if position_value == 0:
            return 0.0
        return (self.unrealized_pnl / position_value) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary."""
        return {
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "unrealized_pnl": self.unrealized_pnl,
            "pnl_percent": self.get_pnl_percent(),
            "entry_time": self.entry_time.isoformat(),
            "trade_id": self.trade_id,
        }


class PositionTracker:
    """
    Tracks all open positions and their real-time P&L.
    
    Responsibilities:
    - Real-time position valuation using current market prices
    - P&L calculation (realized and unrealized)
    - Exit signal monitoring (stop-loss, take-profit, strategy exit)
    - Position exposure reporting
    """
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.realized_pnl_today = 0.0
        
        logger.info("PositionTracker initialized")
    
    def add_position(
        self,
        symbol: str,
        action: str,
        quantity: float,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trade_id: Optional[int] = None,
    ):
        """Add a new position."""
        # Check if position already exists for this symbol
        if symbol in self.positions:
            logger.warning(f"Updating existing position for {symbol}")
            self.close_position(symbol, entry_price, "Position update")
        
        position = Position(
            symbol=symbol,
            action=action,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trade_id=trade_id,
        )
        
        self.positions[symbol] = position
    
    def update_position_price(self, symbol: str, current_price: float):
        """Update current price for a position."""
        if symbol in self.positions:
            self.positions[symbol].update_price(current_price)
    
    def close_position(self, symbol: str, exit_price: float, reason: str = "Manual close") -> Optional[float]:
        """
        Close a position and calculate realized P&L.
        
        Args:
            symbol: Symbol to close
            exit_price: Exit price
            reason: Reason for closure
            
        Returns:
            Realized P&L or None if position doesn't exist
        """
        if symbol not in self.positions:
            logger.warning(f"Attempted to close non-existent position: {symbol}")
            return None
        
        position = self.positions.pop(symbol)
        position.update_price(exit_price)
        realized_pnl = position.unrealized_pnl
        
        self.realized_pnl_today += realized_pnl
        
        logger.info(
            f"Position closed: {position.symbol} | "
            f"Entry: {position.entry_price} | Exit: {exit_price} | "
            f"P&L: {realized_pnl:.2f} ({position.get_pnl_percent():.2f}%) | "
            f"Reason: {reason}"
        )
        
        return realized_pnl
    
    def check_exit_conditions(self, symbol: str) -> Optional[str]:
        """
        Check if position should be exited based on stop-loss or take-profit.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            Exit reason if should exit, None otherwise
        """
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        if position.check_stop_loss_hit():
            return "stop_loss_hit"
        
        if position.check_take_profit_hit():
            return "take_profit_hit"
        
        return None
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position by symbol."""
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """Check if position exists for symbol."""
        return symbol in self.positions
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Get all open positions."""
        return self.positions.copy()
    
    def get_total_unrealized_pnl(self) -> float:
        """Calculate total unrealized P&L across all positions."""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
    
    def get_total_exposure(self) -> float:
        """Calculate total position exposure (sum of position values)."""
        return sum(
            pos.entry_price * pos.quantity 
            for pos in self.positions.values()
        )
    
    def get_position_count(self) -> int:
        """Get number of open positions."""
        return len(self.positions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get position tracker statistics."""
        positions_data = [pos.to_dict() for pos in self.positions.values()]
        
        return {
            "open_positions_count": len(self.positions),
            "total_unrealized_pnl": self.get_total_unrealized_pnl(),
            "total_exposure": self.get_total_exposure(),
            "realized_pnl_today": self.realized_pnl_today,
            "positions": positions_data,
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at start of trading day)."""
        self.realized_pnl_today = 0.0
        logger.info("Daily position stats reset")
