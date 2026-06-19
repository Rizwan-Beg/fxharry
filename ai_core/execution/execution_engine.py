"""Main execution engine for automated trading."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from ai_core.core.logger import get_logger
from ai_core.risk_manager.risk_manager import RiskManager
from ai_core.database.database import SessionLocal
from ai_core.database.models import Trade, AISignal

from .execution_config import (
    ExecutionMode,
    EXECUTION_MODE,
    MAX_ORDERS_PER_MINUTE,
    MAX_ORDER_RETRIES,
    RETRY_DELAY_SECONDS,
    ORDER_TIMEOUT_SECONDS,
    MANUAL_APPROVAL_RISK_THRESHOLD,
    MAX_CONCURRENT_POSITIONS,
)
from .order_manager import OrderManager, OrderState
from .position_tracker import PositionTracker
from .circuit_breaker import CircuitBreaker

logger = get_logger(__name__)


class ExecutionEngine:
    """
    Core execution engine that orchestrates the entire trade lifecycle.
    
    Features:
    - Signal processing and validation
    - Risk management integration
    - Order lifecycle management
    - Position tracking and P&L
    - Paper trading and live trading modes
    - Circuit breaker and safety controls
   
    """
    
    def __init__(
        self,
        broker_service=None,
        risk_manager: Optional[RiskManager] = None,
    ):
        """
        Initialize the execution engine.
        
        Args:
            broker_service: Broker service for order execution (e.g., IBKRService)
            risk_manager: Risk manager instance
        """
        self.broker = broker_service
        self.risk_manager = risk_manager or RiskManager()
        
        self.order_manager = OrderManager()
        self.position_tracker = PositionTracker()
        self.circuit_breaker = CircuitBreaker()
        
        self.execution_mode = EXECUTION_MODE
        self.enabled = True
        self._order_timestamps = []  # For rate limiting
        
        logger.info("=" * 80)
        logger.info("ExecutionEngine initialized")
        logger.info(f"Execution mode: {self.execution_mode.value}")
        logger.info(f"Broker connected: {self.broker is not None}")
        logger.info(f"Risk manager: {type(self.risk_manager).__name__}")
        logger.info("=" * 80)
    
    async def process_signal(self, signal: Dict[str, Any]) -> Optional[int]:
        """
        Process a trading signal and execute if valid.
        
        Args:
            signal: Trading signal from strategy
                Expected format: {
                    'strategy_id': str,
                    'symbol': str,
                    'action': 'LONG' or 'SHORT' or 'EXIT',
                    'price': float,
                    'stop_loss': float (optional),
                    'take_profit': float (optional),
                    'reason': str,
                    'timestamp': str
                }
        
        Returns:
            Trade ID if executed, None otherwise
        """
        try:
            logger.info(f"Processing signal: {signal}")
            
            # Check if execution is enabled
            if not self.enabled:
                logger.warning("Execution engine is disabled")
                return None
            
            # Check circuit breaker
            if self.circuit_breaker.is_tripped:
                logger.warning(
                    f"Circuit breaker is tripped: {self.circuit_breaker.trip_reason}"
                )
                return None
            
            # Validate signal format
            if not self._validate_signal(signal):
                logger.error(f"Invalid signal format: {signal}")
                return None
            
            # Handle exit signals
            if signal['action'] == 'EXIT':
                return await self._process_exit_signal(signal)
            
            # Handle entry signals (LONG/SHORT)
            return await self._process_entry_signal(signal)
            
        except Exception as e:
            logger.error(f"Error processing signal: {e}", exc_info=True)
            return None
    
    
    async def execute_order(
        self,
        symbol: str,
        action: str,
        quantity: int,
        order_type: str = "MKT",
        limit_price: Optional[float] = None,
        strategy_id: str = "MANUAL"
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a manual order (from frontend or API).
        
        This bypasses the signal processing pipeline and executes directly.
        Used for manual trades from Quick Trade panel.
        
        Args:
            symbol: Trading symbol (EUR/USD or EURUSD format)
            action: BUY or SELL
            quantity: Order quantity
            order_type: Order type (currently only MKT supported)
            limit_price: Limit price (for future limit order support)
            strategy_id: Strategy identifier (default: MANUAL)
            
        Returns:
            Order execution result dict or None
        """
        try:
            logger.info(f"🎯 Executing manual order:")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Action: {action}")
            logger.info(f"   Quantity: {quantity}")
            logger.info(f"   Order Type: {order_type}")
            logger.info(f"   Strategy: {strategy_id}")
            
            # Check if execution is enabled
            if not self.enabled:
                logger.warning("❌ Execution engine is disabled")
                return None
            
            # Check circuit breaker
            if self.circuit_breaker.is_tripped:
                logger.warning(f"❌ Circuit breaker is tripped: {self.circuit_breaker.trip_reason}")
                return None
            
            # Validate action
            if action.upper() not in ['BUY', 'SELL']:
                logger.error(f"❌ Invalid action: {action}")
                return None
            
            # Execute through broker if available
            if not self.broker:
                logger.error("❌ No broker service available")
                return None
            
            if self.execution_mode == ExecutionMode.PAPER_TRADING:
                logger.info("📝 [PAPER TRADING] Simulating manual order")
                return {
                    "status": "SIMULATED",
                    "message": f"Paper trading: {action} {quantity} {symbol}",
                    "order_id": f"PAPER-MANUAL-{datetime.now().timestamp()}"
                }
            
            # Execute live trade
            logger.info(f"🚀 [LIVE TRADING] Placing order via broker...")
            result = await self.broker.place_order(
                symbol=symbol,
                action=action.upper(),
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price
            )
            
            if result:
                logger.info(f"✅ Manual order executed successfully: {result}")
                return result
            else:
                logger.error(f"❌ Broker returned no result for manual order")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error executing manual order: {e}", exc_info=True)
            return None
    
    async def process_signals(self, signals: List[Dict[str, Any]]):
        """Process multiple signals (convenience method)."""
        for signal in signals:
            await self.process_signal(signal)
    
    def _validate_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate signal format and required fields."""
        required_fields = ['symbol', 'action', 'price']
        
        for field in required_fields:
            if field not in signal:
                logger.error(f"Signal missing required field: {field}")
                return False
        
        # Validate action
        valid_actions = ['LONG', 'SHORT', 'EXIT', 'BUY', 'SELL']
        if signal['action'] not in valid_actions:
            logger.error(f"Invalid action: {signal['action']}")
            return False
        
        return True
    
    async def _process_entry_signal(self, signal: Dict[str, Any]) -> Optional[int]:
        """Process entry signal (LONG/BUY or SHORT/SELL)."""
        symbol = signal['symbol']
        action_raw = signal['action']
        action = "BUY" if action_raw in ('LONG', 'BUY') else "SELL"
        price = round(signal['price'], 5)
        stop_loss = round(signal.get('stop_loss'), 5) if signal.get('stop_loss') else None
        take_profit = round(signal.get('take_profit'), 5) if signal.get('take_profit') else None
        
        # Check if we already have a position in this symbol
        if self.position_tracker.has_position(symbol):
            logger.warning(f"Already have position in {symbol}, skipping signal")
            return None
        
        # Check position limit
        if self.position_tracker.get_position_count() >= MAX_CONCURRENT_POSITIONS:
            logger.warning(
                f"Max concurrent positions reached "
                f"({MAX_CONCURRENT_POSITIONS}), skipping signal"
            )
            return None
        
        # Get trade score if available
        trade_score = signal.get('trade_score')
        
        # Calculate position size using risk manager
        account_value = await self._get_account_value()
        position_size_info = self.risk_manager.calculate_position_size(
            symbol=symbol,
            entry_price=price,
            stop_loss=stop_loss or price * 0.98,  # Default 2% stop
            risk_percent=0.01,  # Baseline risk 1% per trade
            account_value=account_value,
            trade_score=trade_score
        )
        
        quantity = int(position_size_info.get('quantity', 0))
        
        # Cap position size for forex pairs to reasonable lot sizes
        # Forex: micro lot (1000), mini lot (10000), standard lot (100000)
        MAX_FOREX_QUANTITY = 20000  # 2 mini lots max for safety
        if quantity > MAX_FOREX_QUANTITY:
            logger.info(f"Position size capped: {quantity} -> {MAX_FOREX_QUANTITY} (max forex qty)")
            quantity = MAX_FOREX_QUANTITY
        
        if quantity == 0:
            # If calculator returns 0, use a conservative default
            quantity = 2000  # 2 micro lots as minimum
            logger.info(f"Position size defaulted to {quantity} (calculator returned 0)")
        
        # Assess trade risk
        risk_assessment = self.risk_manager.assess_trade_risk(
            symbol=symbol,
            action=action,
            quantity=quantity,
            entry_price=price,
            account_value=account_value
        )
        
        logger.info(f"Risk assessment for {symbol}: {risk_assessment}")
        
        # Check if trade is approved by risk manager
        if not risk_assessment['approved']:
            logger.warning(
                f"Trade rejected by risk manager: {risk_assessment['warnings']}"
            )
            await self._save_rejected_signal(signal, risk_assessment)
            return None
        
        # Check if manual approval required
        if risk_assessment['risk_score'] > MANUAL_APPROVAL_RISK_THRESHOLD:
            logger.warning(
                f"Trade requires manual approval (risk score: "
                f"{risk_assessment['risk_score']:.2f})"
            )
            # TODO: Implement manual approval queue
            return None
        
        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("Order rate limit exceeded")
            return None
        
        # Create order
        order = self.order_manager.create_order(
            signal=signal,
            symbol=symbol,
            action=action,
            quantity=quantity,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        
        # Approve order
        self.order_manager.approve_order(order.order_id)
        
        # Execute order
        trade_id = await self._execute_order(order, risk_assessment)
        
        return trade_id
    
    async def _process_exit_signal(self, signal: Dict[str, Any]) -> Optional[int]:
        """Process exit signal to close existing position."""
        symbol = signal['symbol']
        
        if not self.position_tracker.has_position(symbol):
            logger.warning(f"No position to exit for {symbol}")
            return None
        
        position = self.position_tracker.get_position(symbol)
        exit_price = signal['price']
        exit_action = "SELL" if position.action == "BUY" else "BUY"
        
        # Close position
        realized_pnl = self.position_tracker.close_position(
            symbol=symbol,
            exit_price=exit_price,
            reason=signal.get('reason', 'Strategy exit signal')
        )
        
        # Update circuit breaker
        if realized_pnl is not None:
            account_value = await self._get_account_value()
            total_pnl = self.position_tracker.realized_pnl_today
            self.circuit_breaker.check_and_update(
                daily_pnl=total_pnl,
                account_equity=account_value,
                last_trade_profitable=(realized_pnl > 0)
            )
        
        # Execute exit order if in live mode
        if self.execution_mode == ExecutionMode.LIVE_TRADING and self.broker:
            try:
                result = await self.broker.place_order(
                    symbol=symbol,
                    action=exit_action,
                    quantity=position.quantity,
                    order_type="MKT"
                )
                logger.info(f"Exit order placed: {result}")
            except Exception as e:
                logger.error(f"Error placing exit order: {e}")
        
        # Update database
        await self._update_trade_exit(position.trade_id, exit_price, realized_pnl)
        
        return position.trade_id
    
    async def _execute_order(
        self,
        order,
        risk_assessment: Dict[str, Any]
    ) -> Optional[int]:
        """
        Execute an order through the broker or simulate in paper mode.
        
        Args:
            order: Order to execute
            risk_assessment: Risk assessment results
            
        Returns:
            Trade ID if successful, None otherwise
        """
        try:
            # Save to database first
            trade_id = await self._save_trade_to_db(order, risk_assessment)
            
            if self.execution_mode == ExecutionMode.PAPER_TRADING:
                # Paper trading: simulate execution
                logger.info(f"[PAPER TRADING] Simulating order: {order.to_dict()}")
                order.broker_order_id = f"PAPER-{order.order_id}"
                self.order_manager.submit_order(order.order_id, order.broker_order_id)
                
                # Simulate immediate fill
                self.order_manager.fill_order(
                    order_id=order.order_id,
                    filled_quantity=order.quantity,
                    avg_fill_price=order.entry_price,
                    partial=False
                )
                
                # Add to position tracker
                self.position_tracker.add_position(
                    symbol=order.symbol,
                    action=order.action,
                    quantity=order.quantity,
                    entry_price=order.entry_price,
                    stop_loss=order.stop_loss,
                    take_profit=order.take_profit,
                    trade_id=trade_id
                )
                
                logger.info(f"[PAPER TRADING] Order filled: {order.order_id}")
                
            elif self.execution_mode == ExecutionMode.LIVE_TRADING:
                # Live trading: execute through broker
                if not self.broker:
                    logger.error("No broker service available for live trading")
                    self.order_manager.fail_order(
                        order.order_id,
                        "No broker service"
                    )
                    return None
                
                logger.info(f"[LIVE TRADING] Placing order: {order.to_dict()}")
                
                result = await self.broker.place_order(
                    symbol=self._normalize_symbol(order.symbol),
                    action=order.action,
                    quantity=order.quantity,
                    order_type="MKT",
                    stop_loss=order.stop_loss,
                    take_profit=order.take_profit,
                )
                
                if result:
                    broker_order_id = result.get('order_id') or result.get('parent_order_id')
                    self.order_manager.submit_order(order.order_id, broker_order_id)
                    
                    # Add to position tracker (will be updated when fill confirmed)
                    self.position_tracker.add_position(
                        symbol=order.symbol,
                        action=order.action,
                        quantity=order.quantity,
                        entry_price=order.entry_price,
                        stop_loss=order.stop_loss,
                        take_profit=order.take_profit,
                        trade_id=trade_id
                    )
                    
                    logger.info(f"[LIVE TRADING] Order submitted: {broker_order_id}")
                else:
                    logger.error("Broker returned no result")
                    self.order_manager.fail_order(order.order_id, "Broker returned no result")
                    return None
            
            # Update order timestamps for rate limiting
            self._order_timestamps.append(datetime.now())
            
            return trade_id
            
        except Exception as e:
            logger.error(f"Error executing order: {e}", exc_info=True)
            self.order_manager.fail_order(order.order_id, str(e))
            return None
    
    async def _save_trade_to_db(
        self,
        order,
        risk_assessment: Dict[str, Any]
    ) -> int:
        """Save trade to database."""
        db = SessionLocal()
        try:
            trade = Trade(
                strategy_id=1,  # TODO: Get from signal
                symbol=order.symbol,
                action=order.action,
                quantity=order.quantity,
                entry_price=order.entry_price,
                stop_loss=order.stop_loss,
                take_profit=order.take_profit,
                status='OPEN',
                risk_score=risk_assessment['risk_score'],
                position_size_percent=risk_assessment['position_size_percent'],
            )
            
            db.add(trade)
            db.commit()
            db.refresh(trade)
            
            logger.info(f"Trade saved to database: ID={trade.id}")
            return trade.id
            
        finally:
            db.close()
    
    async def _update_trade_exit(
        self,
        trade_id: Optional[int],
        exit_price: float,
        pnl: float
    ):
        """Update trade with exit information."""
        if not trade_id:
            return
        
        db = SessionLocal()
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                trade.exit_price = exit_price
                trade.pnl = pnl
                trade.status = 'CLOSED'
                trade.exit_time = datetime.now()
                db.commit()
                logger.info(f"Trade {trade_id} updated with exit info")
        finally:
            db.close()
    
    async def sync_trades_with_broker(self):
        """
        Sync trade database with actual broker positions.
        
        Detects trades marked OPEN in DB that are no longer held
        by the broker, and marks them as CLOSED.
        """
        if not self.broker:
            return
        
        try:
            # Get current broker positions
            broker_positions = await self.broker.get_positions()
            if broker_positions is None:
                broker_positions = []
            
            # Build set of symbols currently held at broker
            broker_symbols = set()
            for pos in broker_positions:
                sym = pos.get('symbol', '') if isinstance(pos, dict) else str(pos)
                # Normalize: EURUSD -> EUR/USD
                if len(sym) == 6 and '/' not in sym:
                    sym = f"{sym[:3]}/{sym[3:]}"
                broker_symbols.add(sym)
            
            # Check DB for OPEN trades not held by broker
            db = SessionLocal()
            try:
                open_trades = db.query(Trade).filter(Trade.status == 'OPEN').all()
                
                for trade in open_trades:
                    trade_sym = trade.symbol
                    # Normalize symbol for comparison
                    if len(trade_sym) == 6 and '/' not in trade_sym:
                        trade_sym_norm = f"{trade_sym[:3]}/{trade_sym[3:]}"
                    else:
                        trade_sym_norm = trade_sym
                    
                    if trade_sym_norm not in broker_symbols and trade_sym not in broker_symbols:
                        # Position no longer held at broker — mark as closed
                        trade.status = 'CLOSED'
                        trade.exit_time = datetime.now()
                        # Use entry_price as exit if we don't have a better one
                        if trade.exit_price is None:
                            trade.exit_price = trade.entry_price  
                        if trade.pnl is None:
                            trade.pnl = 0.0
                        logger.info(
                            f"📊 Trade sync: Marked trade #{trade.id} ({trade.symbol}) as CLOSED "
                            f"(no longer in broker positions)"
                        )
                        # Remove it from our in-memory tracker so we can take new trades!
                        if self.position_tracker.has_position(trade.symbol):
                            self.position_tracker.close_position(
                                symbol=trade.symbol, 
                                exit_price=trade.exit_price, 
                                reason="Sync: Closed at Broker"
                            )
                
                db.commit()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error syncing trades with broker: {e}", exc_info=True)
    
    async def _save_rejected_signal(
        self,
        signal: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ):
        """Save rejected signal to database for analysis."""
        db = SessionLocal()
        try:
            ai_signal = AISignal(
                strategy_id=1,  # TODO: Get from signal
                symbol=signal['symbol'],
                signal_type=signal['action'],
                confidence=1.0,
                price=signal['price'],
                is_executed=False,
            )
            db.add(ai_signal)
            db.commit()
            logger.debug(f"Rejected signal saved: {signal['symbol']}")
        except Exception as e:
            logger.error(f"Error saving rejected signal: {e}")
        finally:
            db.close()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within order rate limits."""
        now = datetime.now()
        # Remove timestamps older than 1 minute
        self._order_timestamps = [
            ts for ts in self._order_timestamps 
            if (now - ts).total_seconds() < 60
        ]
        
        return len(self._order_timestamps) < MAX_ORDERS_PER_MINUTE
    
    async def _get_account_value(self) -> float:
        """Get current account value."""
        # TODO: Get from broker or database
        return 100000.0  # Default for now
    
    def update_position_prices(self, market_data: Dict[str, float]):
        """
        Update position prices with latest market data.
        
        Args:
            market_data: Dict of symbol -> current_price
        """
        for symbol, price in market_data.items():
            self.position_tracker.update_position_price(symbol, price)
            
            # Check exit conditions
            exit_reason = self.position_tracker.check_exit_conditions(symbol)
            if exit_reason:
                logger.info(f"Exit condition triggered for {symbol}: {exit_reason}")
                # Create exit signal
                asyncio.create_task(self.process_signal({
                    'symbol': symbol,
                    'action': 'EXIT',
                    'price': price,
                    'reason': exit_reason,
                    'timestamp': datetime.now().isoformat()
                }))
    
    def emergency_stop(self):
        """Emergency stop - halt all trading immediately."""
        logger.critical("=" * 80)
        logger.critical("🚨 EMERGENCY STOP ACTIVATED 🚨")
        logger.critical("=" * 80)
        
        self.circuit_breaker.manual_trip("Emergency stop by user")
        self.enabled = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get execution engine status."""
        return {
            "enabled": self.enabled,
            "execution_mode": self.execution_mode.value,
            "circuit_breaker": self.circuit_breaker.get_status(),
            "orders": self.order_manager.get_stats(),
            "positions": self.position_tracker.get_stats(),
        }

    def _normalize_symbol(self, symbol: str) -> str:
        return symbol.replace("/", "")
