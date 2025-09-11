import asyncio
import threading
import queue
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import logging

logger = logging.getLogger(__name__)

class IBKRWrapper(EWrapper):
    """IB API Wrapper"""
    
    def __init__(self):
        EWrapper.__init__(self)
        self.data_queue = queue.Queue()
        self.market_data = {}
        self.positions = {}
        self.account_data = {}
        self.orders = {}
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        logger.error(f"IBKR Error - ReqId: {reqId}, Code: {errorCode}, Msg: {errorString}")
        
    def tickPrice(self, reqId, tickType, price, attrib):
        """Handle tick price updates"""
        symbol = self._get_symbol_from_req_id(reqId)
        if symbol not in self.market_data:
            self.market_data[symbol] = {}
            
        if tickType == 1:  # BID
            self.market_data[symbol]['bid'] = price
        elif tickType == 2:  # ASK
            self.market_data[symbol]['ask'] = price
        elif tickType == 4:  # LAST
            self.market_data[symbol]['last'] = price
            
        # Calculate spread
        if 'bid' in self.market_data[symbol] and 'ask' in self.market_data[symbol]:
            self.market_data[symbol]['spread'] = (
                self.market_data[symbol]['ask'] - self.market_data[symbol]['bid']
            )
        
        # Queue update for broadcasting
        self.data_queue.put({
            'type': 'tick_price',
            'symbol': symbol,
            'data': self.market_data[symbol].copy(),
            'timestamp': datetime.now().isoformat()
        })
    
    def tickSize(self, reqId, tickType, size):
        """Handle tick size updates"""
        symbol = self._get_symbol_from_req_id(reqId)
        if symbol not in self.market_data:
            self.market_data[symbol] = {}
            
        if tickType == 0:  # BID_SIZE
            self.market_data[symbol]['bid_size'] = size
        elif tickType == 3:  # ASK_SIZE
            self.market_data[symbol]['ask_size'] = size
    
    def position(self, account, contract, position, avgCost):
        """Handle position updates"""
        symbol = contract.symbol
        self.positions[symbol] = {
            'symbol': symbol,
            'position': position,
            'avg_cost': avgCost,
            'market_value': position * avgCost,
            'currency': contract.currency
        }
    
    def accountSummary(self, reqId, account, tag, value, currency):
        """Handle account summary updates"""
        self.account_data[tag] = {
            'value': value,
            'currency': currency,
            'timestamp': datetime.now().isoformat()
        }
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, 
                   permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        """Handle order status updates"""
        self.orders[orderId] = {
            'status': status,
            'filled': filled,
            'remaining': remaining,
            'avg_fill_price': avgFillPrice,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_symbol_from_req_id(self, req_id: int) -> str:
        """Map request ID to symbol - simplified implementation"""
        symbol_map = {
            1000: 'EURUSD',
            1001: 'GBPUSD', 
            1002: 'XAUUSD',
            1003: 'USDJPY',
            1004: 'USDCAD'
        }
        return symbol_map.get(req_id, 'UNKNOWN')

class IBKRService:
    """Interactive Brokers service for trading operations"""
    
    def __init__(self, host="127.0.0.1", port=7497, client_id=1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.wrapper = IBKRWrapper()
        self.client = EClient(self.wrapper)
        self.connected = False
        self.thread = None
        
    async def initialize(self) -> bool:
        """Initialize connection to IB Gateway/TWS"""
        try:
            # Connect to IB in a separate thread
            self.thread = threading.Thread(target=self._connect_and_run)
            self.thread.daemon = True
            self.thread.start()
            
            # Wait for connection
            await asyncio.sleep(2)
            
            if self.client.isConnected():
                self.connected = True
                logger.info("Connected to Interactive Brokers")
                
                # Request account summary
                self.client.reqAccountSummary(9001, "All", 
                    "TotalCashValue,StockMarketValue,NetLiquidation,BuyingPower")
                
                # Request positions
                self.client.reqPositions()
                
                return True
            else:
                logger.error("Failed to connect to Interactive Brokers")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing IBKR service: {e}")
            return False
    
    def _connect_and_run(self):
        """Connect and run the client in a separate thread"""
        try:
            self.client.connect(self.host, self.port, self.client_id)
            self.client.run()
        except Exception as e:
            logger.error(f"IBKR connection error: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to IB"""
        return self.connected and self.client.isConnected()
    
    async def subscribe_market_data(self, symbols: List[str]):
        """Subscribe to real-time market data"""
        if not self.is_connected():
            logger.error("Not connected to IBKR")
            return False
        
        try:
            symbol_to_req_id = {
                'EURUSD': 1000,
                'GBPUSD': 1001,
                'XAUUSD': 1002,
                'USDJPY': 1003,
                'USDCAD': 1004
            }
            
            for symbol in symbols:
                if symbol in symbol_to_req_id:
                    contract = self._create_forex_contract(symbol)
                    req_id = symbol_to_req_id[symbol]
                    
                    self.client.reqMktData(req_id, contract, "", False, False, [])
                    logger.info(f"Subscribed to market data for {symbol}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to market data: {e}")
            return False
    
    def _create_forex_contract(self, symbol: str) -> Contract:
        """Create forex contract for IB API"""
        contract = Contract()
        
        if symbol == 'XAUUSD':
            # Gold futures or CFD
            contract.symbol = "XAUUSD"
            contract.secType = "CFD"
            contract.exchange = "SMART"
            contract.currency = "USD"
        else:
            # Regular forex pairs
            if len(symbol) == 6:
                base_currency = symbol[:3]
                quote_currency = symbol[3:]
                
                contract.symbol = base_currency
                contract.secType = "CASH"
                contract.currency = quote_currency
                contract.exchange = "IDEALPRO"
        
        return contract
    
    async def place_order(self, symbol: str, action: str, quantity: float, 
                         order_type: str = "MKT", limit_price: Optional[float] = None,
                         stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Optional[int]:
        """Place a trading order"""
        if not self.is_connected():
            logger.error("Not connected to IBKR")
            return None
        
        try:
            contract = self._create_forex_contract(symbol)
            order = Order()
            
            order.action = action.upper()
            order.orderType = order_type
            order.totalQuantity = quantity
            
            if order_type == "LMT" and limit_price:
                order.lmtPrice = limit_price
            
            # Add stop loss and take profit as bracket orders
            if stop_loss or take_profit:
                order.transmit = False  # Don't transmit parent order yet
                
                parent_order_id = self.client.getReqId()
                order.orderId = parent_order_id
                order.transmit = not (stop_loss or take_profit)
                
                # Place parent order
                self.client.placeOrder(parent_order_id, contract, order)
                
                # Add stop loss order
                if stop_loss:
                    stop_order = Order()
                    stop_order.action = "SELL" if action.upper() == "BUY" else "BUY"
                    stop_order.orderType = "STP"
                    stop_order.auxPrice = stop_loss
                    stop_order.totalQuantity = quantity
                    stop_order.parentId = parent_order_id
                    stop_order.transmit = not take_profit
                    
                    stop_order_id = self.client.getReqId()
                    self.client.placeOrder(stop_order_id, contract, stop_order)
                
                # Add take profit order
                if take_profit:
                    profit_order = Order()
                    profit_order.action = "SELL" if action.upper() == "BUY" else "BUY"
                    profit_order.orderType = "LMT"
                    profit_order.lmtPrice = take_profit
                    profit_order.totalQuantity = quantity
                    profit_order.parentId = parent_order_id
                    profit_order.transmit = True
                    
                    profit_order_id = self.client.getReqId()
                    self.client.placeOrder(profit_order_id, contract, profit_order)
                
                return parent_order_id
            else:
                order_id = self.client.getReqId()
                order.orderId = order_id
                self.client.placeOrder(order_id, contract, order)
                return order_id
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get current market data"""
        return self.wrapper.market_data.copy()
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        return self.wrapper.positions.copy()
    
    def get_account_data(self) -> Dict[str, Any]:
        """Get account information"""
        return self.wrapper.account_data.copy()
    
    def get_pending_data_updates(self) -> List[Dict]:
        """Get pending data updates from queue"""
        updates = []
        try:
            while True:
                update = self.wrapper.data_queue.get_nowait()
                updates.append(update)
        except queue.Empty:
            pass
        return updates
    
    async def disconnect(self):
        """Disconnect from IB"""
        if self.client.isConnected():
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from Interactive Brokers")