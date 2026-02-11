"""Order lifecycle management."""

from enum import Enum
from datetime import datetime
from typing import Dict, Optional, Any
import time
from ai_core.core.logger import get_logger

logger = get_logger(__name__)


class OrderState(Enum):
    """Order lifecycle states."""
    PENDING = "PENDING"              # Signal received, awaiting validation
    APPROVED = "APPROVED"            # Risk check passed, ready to submit
    SUBMITTED = "SUBMITTED"          # Sent to broker
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Partial execution
    FILLED = "FILLED"                # Fully executed
    CANCELLED = "CANCELLED"          # Order cancelled
    REJECTED = "REJECTED"            # Rejected by broker or risk manager
    FAILED = "FAILED"                # Technical failure


class Order:
    """Represents a trading order with full lifecycle tracking."""
    
    def __init__(
        self,
        signal: Dict[str, Any],
        symbol: str,
        action: str,
        quantity: float,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ):
        self.order_id = self._generate_order_id()
        self.signal = signal
        self.symbol = symbol
        self.action = action.upper()  # BUY or SELL
        self.quantity = quantity
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        
        self.state = OrderState.PENDING
        self.broker_order_id = None
        self.filled_quantity = 0.0
        self.avg_fill_price = 0.0
        self.rejection_reason = None
        
        self.created_time = datetime.now()
        self.submitted_time = None
        self.filled_time = None
        
        self.retry_count = 0
        self.state_history = [(OrderState.PENDING, datetime.now(), "Order created")]
        
        logger.debug(f"Created order {self.order_id}: {action} {quantity} {symbol} @ {entry_price}")
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID."""
        timestamp = int(time.time() * 1000)
        return f"ORD-{timestamp}"
    
    def transition_to(self, new_state: OrderState, reason: str = ""):
        """
        Transition order to new state.
        
        Args:
            new_state: Target state
            reason: Reason for transition
        """
        old_state = self.state
        self.state = new_state
        self.state_history.append((new_state, datetime.now(), reason))
        
        # Update timestamps
        if new_state == OrderState.SUBMITTED:
            self.submitted_time = datetime.now()
        elif new_state == OrderState.FILLED:
            self.filled_time = datetime.now()
        
        logger.info(f"Order {self.order_id} transitioned: {old_state.value} → {new_state.value} ({reason})")
    
    def is_terminal_state(self) -> bool:
        """Check if order is in a terminal state (no further transitions)."""
        return self.state in [
            OrderState.FILLED,
            OrderState.CANCELLED,
            OrderState.REJECTED,
            OrderState.FAILED
        ]
    
    def is_active(self) -> bool:
        """Check if order is actively being processed."""
        return self.state in [
            OrderState.PENDING,
            OrderState.APPROVED,
            OrderState.SUBMITTED,
            OrderState.PARTIALLY_FILLED
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return {
            "order_id": self.order_id,
            "broker_order_id": self.broker_order_id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "filled_quantity": self.filled_quantity,
            "entry_price": self.entry_price,
            "avg_fill_price": self.avg_fill_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "state": self.state.value,
            "rejection_reason": self.rejection_reason,
            "created_time": self.created_time.isoformat(),
            "submitted_time": self.submitted_time.isoformat() if self.submitted_time else None,
            "filled_time": self.filled_time.isoformat() if self.filled_time else None,
            "retry_count": self.retry_count,
        }


class OrderManager:
    """
    Manages order lifecycle and state transitions.
    
    Responsibilities:
    - Order state machine management
    - Retry logic for transient failures
    - Timeout handling
    - Order status synchronization with broker
    """
    
    def __init__(self):
        self.active_orders: Dict[str, Order] = {}
        self.completed_orders: Dict[str, Order] = {}
        
        logger.info("OrderManager initialized")
    
    def create_order(
        self,
        signal: Dict[str, Any],
        symbol: str,
        action: str,
        quantity: float,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Order:
        """
        Create a new order from a trading signal.
        
        Args:
            signal: Original trading signal
            symbol: Trading symbol
            action: BUY or SELL
            quantity: Order quantity
            entry_price: Entry price
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            
        Returns:
            Created order
        """
        order = Order(
            signal=signal,
            symbol=symbol,
            action=action,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        
        self.active_orders[order.order_id] = order
        return order
    
    def approve_order(self, order_id: str):
        """Mark order as approved (risk checks passed)."""
        if order_id in self.active_orders:
            self.active_orders[order_id].transition_to(
                OrderState.APPROVED,
                "Risk validation passed"
            )
    
    def submit_order(self, order_id: str, broker_order_id: Optional[str] = None):
        """Mark order as submitted to broker."""
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            if broker_order_id:
                order.broker_order_id = broker_order_id
            order.transition_to(OrderState.SUBMITTED, "Submitted to broker")
    
    def fill_order(
        self,
        order_id: str,
        filled_quantity: float,
        avg_fill_price: float,
        partial: bool = False
    ):
        """
        Mark order as filled (fully or partially).
        
        Args:
            order_id: Order ID
            filled_quantity: Quantity filled
            avg_fill_price: Average fill price
            partial: Whether this is a partial fill
        """
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order.filled_quantity = filled_quantity
            order.avg_fill_price = avg_fill_price
            
            if partial:
                order.transition_to(OrderState.PARTIALLY_FILLED, "Partial fill received")
            else:
                order.transition_to(OrderState.FILLED, "Order fully filled")
                self._move_to_completed(order_id)
    
    def reject_order(self, order_id: str, reason: str):
        """Reject an order."""
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order.rejection_reason = reason
            order.transition_to(OrderState.REJECTED, reason)
            self._move_to_completed(order_id)
    
    def cancel_order(self, order_id: str, reason: str = "User cancellation"):
        """Cancel an order."""
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order.transition_to(OrderState.CANCELLED, reason)
            self._move_to_completed(order_id)
    
    def fail_order(self, order_id: str, reason: str):
        """Mark order as failed due to technical error."""
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order.transition_to(OrderState.FAILED, reason)
            
            # Don't immediately move to completed - may retry
            order.retry_count += 1
    
    def increment_retry(self, order_id: str):
        """Increment retry count for an order."""
        if order_id in self.active_orders:
            self.active_orders[order_id].retry_count += 1
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID (checks both active and completed)."""
        if order_id in self.active_orders:
            return self.active_orders[order_id]
        return self.completed_orders.get(order_id)
    
    def get_active_orders(self) -> Dict[str, Order]:
        """Get all active orders."""
        return self.active_orders.copy()
    
    def _move_to_completed(self, order_id: str):
        """Move order from active to completed."""
        if order_id in self.active_orders:
            order = self.active_orders.pop(order_id)
            self.completed_orders[order_id] = order
            logger.debug(f"Order {order_id} moved to completed ({order.state.value})")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get order manager statistics."""
        return {
            "active_orders": len(self.active_orders),
            "completed_orders": len(self.completed_orders),
            "active_order_ids": list(self.active_orders.keys()),
        }
