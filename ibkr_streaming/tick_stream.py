# ibkr_streaming/tick_stream.py

import time
from ib_async import Ticker
from .ibkr_client import connect_ibkr
from .symbols import SYMBOLS
from .logger import get_logger

logger = get_logger(__name__)

class TickStreamer:
    def __init__(self, ib=None):
        self.ib = ib
        self.subscribed = {}
        logger.info("TickStreamer instance created")

    async def initialize(self):
        """Async initialization to connect to IBKR"""
        logger.debug("Initializing TickStreamer connection")
        if self.ib is None:
            logger.info("IB instance not provided, creating new connection")
            # connect_ibkr() is synchronous but nest_asyncio allows this in async context
            self.ib = connect_ibkr()
        else:
            logger.info("Using provided IB instance")
        logger.info(f"TickStreamer initialized. Connection status: {self.ib.isConnected()}")

    async def start(self):
        """Start streaming - qualify contracts first, then subscribe"""
        logger.info("=" * 80)
        logger.info("Starting Market Data Subscription Process")
        logger.info(f"Symbols to subscribe: {list(SYMBOLS.keys())}")
        
        # Qualify contracts to get conId (required for hashing)
        contracts = list(SYMBOLS.values())
        logger.debug(f"Qualifying {len(contracts)} contracts...")
        
        try:
            qualified = await self.ib.qualifyContractsAsync(*contracts)
            logger.info(f"Contract qualification completed. Received {len(qualified)} qualified contracts")
        except Exception as e:
            logger.error(f"Failed to qualify contracts: {e}", exc_info=True)
            raise
        
        # Create a mapping from symbol to qualified contract
        symbol_to_contract = {}
        for i, (sym, contract) in enumerate(SYMBOLS.items()):
            # Match by index (qualified list should match input order)
            if i < len(qualified) and qualified[i] is not None:
                symbol_to_contract[sym] = qualified[i]
                q_contract = qualified[i]
                logger.info(f"✅ Qualified: {sym} | ConId: {q_contract.conId} | Exchange: {q_contract.exchange}")
            else:
                logger.warning(f"⚠️  Could not qualify {sym}, skipping subscription")
        
        logger.info(f"Successfully qualified {len(symbol_to_contract)} out of {len(SYMBOLS)} contracts")
        
        # Subscribe to market data with qualified contracts
        subscription_count = 0
        for sym, contract in symbol_to_contract.items():
            try:
                logger.debug(f"Requesting market data for {sym}...")
                ticker: Ticker = self.ib.reqMktData(contract, '', False, False)
                self.subscribed[sym] = ticker
                subscription_count += 1
                logger.info(f"📡 Subscribed to market data: {sym} | Contract ID: {contract.conId}")
            except Exception as e:
                logger.error(f"❌ Error subscribing to {sym}: {e}", exc_info=True)
        
        logger.info(f"Market data subscription complete: {subscription_count}/{len(symbol_to_contract)} successful")
        logger.info("=" * 80)

    def get_ticks(self):
        """Retrieve current tick data for all subscribed symbols"""
        import math
        ticks = {}
        for sym, ticker in self.subscribed.items():
            try:
                # Get raw values and check for NaN/None
                raw_bid = ticker.bid
                raw_ask = ticker.ask
                
                # Filter out NaN, None, or invalid values
                if raw_bid is None or (isinstance(raw_bid, float) and math.isnan(raw_bid)):
                    continue  # Skip this tick if bid is invalid
                if raw_ask is None or (isinstance(raw_ask, float) and math.isnan(raw_ask)):
                    continue  # Skip this tick if ask is invalid
                
                bid = float(raw_bid)
                ask = float(raw_ask)
                
                # Validate prices are positive and reasonable
                if bid <= 0 or ask <= 0 or ask < bid:
                    logger.warning(f"Invalid price data for {sym}: bid={bid}, ask={ask}")
                    continue
                
                mid = (bid + ask) / 2.0
                spread = ask - bid

                ticks[sym] = {
                    "symbol": sym,
                    "bid": bid,
                    "ask": ask,
                    "mid": mid,
                    "spread": spread,
                    "timestamp": time.time()
                }
                
                # Log tick data at DEBUG level (can be enabled for detailed tracking)
                logger.debug(f"Tick: {sym} | Bid: {bid} | Ask: {ask} | Mid: {mid}")
            except Exception as e:
                logger.warning(f"Error retrieving tick for {sym}: {e}")
                # Don't add invalid ticks to the result
        
        return ticks
