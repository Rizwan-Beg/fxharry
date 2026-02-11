"""
IBKR Broker Service using ib_async library.
This adapter wraps ib_async to implement the BaseBroker interface.
"""

import asyncio
from typing import Dict, List, Optional, Any
from ib_async import IB, CFD, Forex, MarketOrder, util
from ai_core.core.logger import get_logger
from .base_broker import BaseBroker

logger = get_logger(__name__)


class IBKRAsyncService(BaseBroker):
    """Interactive Brokers service using ib_async library."""
    
    name = "ibkr_async"

    def __init__(self, host="127.0.0.1", port=7497, client_id=998):
        """
        Initialize IBKR async service.
        
        Args:
            host: IBKR TWS/Gateway host
            port: IBKR TWS/Gateway port (7497 for paper, 7496 for live)
            client_id: Unique client ID for this connection
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False
        
        # Start event loop if not already running
        try:
            util.startLoop()
        except RuntimeError:
            # Loop already running
            pass
    
    async def connect(self) -> None:
        """Establish connection to IBKR TWS/Gateway."""
        try:
            logger.info(f"Connecting to IBKR at {self.host}:{self.port} with client ID {self.client_id}")
            
            # Connect to IBKR
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            
            # Wait a moment for connection to stabilize
            await asyncio.sleep(1)
            
            if self.ib.isConnected():
                self.connected = True
                logger.info("✅ Successfully connected to IBKR TWS/Gateway")
                
                # Log account info
                accounts = self.ib.managedAccounts()
                logger.info(f"Connected to accounts: {accounts}")
            else:
                raise RuntimeError("Failed to connect to IBKR")
                
        except Exception as e:
            logger.error(f"Error connecting to IBKR: {e}", exc_info=True)
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from IBKR."""
        if self.ib.isConnected():
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR")
    
    def _create_contract(self, symbol: str) -> Any:
        """
        Create IBKR contract for a given symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'EUR/USD', 'EURUSD')
            
        Returns:
            ib_async contract object
        """
        # Normalize symbol
        symbol = symbol.replace("/", "").upper()
        
        # For forex pairs, use CFD contracts (proven to work)
        if len(symbol) == 6:
            base_currency = symbol[:3]
            quote_currency = symbol[3:]
            
            # Use CFD for forex (matches our successful test)
            contract = CFD(base_currency, currency=quote_currency)
            
            # Qualify the contract to get full details
            contracts = self.ib.qualifyContracts(contract)
            if contracts:
                return contracts[0]
            else:
                logger.warning(f"Could not qualify contract for {symbol}, using unqualified")
                return contract
        else:
            # For other instruments, use Forex
            contract = Forex(symbol)
            contracts = self.ib.qualifyContracts(contract)
            return contracts[0] if contracts else contract
    
    async def place_order(
        self,
        symbol: str,
        action: str,
        quantity: float,
        order_type: str = "MKT",
        limit_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Place a trading order.
        
        Args:
            symbol: Trading symbol (e.g., 'EUR/USD')
            action: 'BUY' or 'SELL'
            quantity: Order quantity
            order_type: Order type ('MKT', 'LMT', etc.)
            limit_price: Limit price for limit orders
            stop_loss: Stop loss price (not currently supported)
            take_profit: Take profit price (not currently supported)
            
        Returns:
            Dict with order details or None if failed
        """
        if not self.connected or not self.ib.isConnected():
            logger.error("Not connected to IBKR")
            return None
        
        try:
            # Create contract
            contract = self._create_contract(symbol)
            logger.info(f"Created contract: {contract}")
            
            # Create order
            if order_type == "MKT":
                order = MarketOrder(action=action.upper(), totalQuantity=quantity)
            else:
                logger.error(f"Order type {order_type} not yet supported")
                return None
            
            logger.info(f"Placing {action} order for {quantity} {symbol}")
            
            # Place order
            trade = self.ib.placeOrder(contract, order)
            
            # Wait a bit for order to be processed
            await asyncio.sleep(2)
            
            # Check trade status
            logger.info(f"Order placed: {trade}")
            logger.info(f"Order status: {trade.orderStatus.status}")
            
            # Return order details
            return {
                "order_id": trade.order.orderId,
                "perm_id": trade.order.permId,
                "status": trade.orderStatus.status,
                "filled": trade.orderStatus.filled,
                "remaining": trade.orderStatus.remaining,
                "avg_fill_price": trade.orderStatus.avgFillPrice,
                "contract": {
                    "symbol": contract.symbol,
                    "conId": contract.conId,
                    "currency": contract.currency,
                },
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}", exc_info=True)
            return None
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions from IBKR.
        
        Returns:
            List of position dictionaries
        """
        if not self.connected or not self.ib.isConnected():
            logger.warning("Not connected to IBKR")
            return []
        
        try:
            positions = self.ib.positions()
            
            result = []
            for pos in positions:
                result.append({
                    "account": pos.account,
                    "symbol": pos.contract.symbol,
                    "position": pos.position,
                    "avg_cost": pos.avgCost,
                    "currency": pos.contract.currency,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}", exc_info=True)
            return []
    
    async def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary (NetLiquidation, BuyingPower, etc.)
        """
        if not self.connected or not self.ib.isConnected():
            logger.warning("Not connected to IBKR")
            return {}

        try:
            # Use accountValues() which is more reliable and avoids signature issues
            summaries = self.ib.accountValues()
            
            result = {}
            for s in summaries:
                # s has tag, value, currency, account
                if hasattr(s, 'tag') and hasattr(s, 'value'):
                    # Prefer values with matching currency if possible
                    # IBKR often returns values in 'BASE' currency (the account's currency)
                    # and sometimes in specific currencies.
                    # We want the value where currency matches the account's base currency.
                    
                    # If we already have this tag...
                    if s.tag in result:
                        # If the new one is USD or has no currency, maybe keep it?
                        # Actually, typically we want the one with currency='BASE' (if IB returns that)
                        # or the one matching the user's account currency.
                        # For now, let's log what we see for NetLiquidation to debug
                        if s.tag == "NetLiquidation":
                            logger.info(f"Account Value: {s.tag}={s.value} ({s.currency})")
                            
                        # Simple logic: If we have a value and the new one is NOT the base currency, skip
                        # But we don't know base currency easily without checking. 
                        # Let's assume the LAST one is usually the base or we prioritize specific currencies.
                        # Better approach: Store all and let frontend decide? No, frontend expects simple dict.
                        
                        # PRIORITY: specific currency > empty currency
                        if s.currency:
                             result[s.tag] = s.value # Overwrite with specific currency version
                    else:
                        result[s.tag] = s.value
            
            return result

        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}

    async def health(self) -> Dict[str, Any]:
        """Get broker health status."""
        return {
            "name": self.name,
            "status": "connected" if self.connected and self.ib.isConnected() else "disconnected",
            "host": self.host,
            "port": self.port,
            "client_id": self.client_id,
        }

