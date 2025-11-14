# ibkr_streaming/run.py

import asyncio
import signal
import sys
import time
from datetime import datetime
import nest_asyncio
nest_asyncio.apply()
from .tick_stream import TickStreamer
from .candle_engine import CandleEngine
from .microstructure import compute_microstructure
from .ws_push import push
from .logger import get_logger

logger = get_logger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_flag
    logger.info("=" * 80)
    logger.info("Shutdown signal received. Initiating graceful shutdown...")
    shutdown_flag = True

async def main():
    """Main execution loop for IBKR streaming service"""
    global shutdown_flag
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 80)
    logger.info("IBKR Streaming Service Starting")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    tick_count = 0  # Initialize before try block for finally clause
    iteration = 0
    
    try:
        # Initialize components
        logger.info("Initializing TickStreamer...")
        tick_stream = TickStreamer()
        await tick_stream.initialize()
        
        logger.info("Initializing CandleEngine...")
        candle_engine = CandleEngine()
        
        logger.info("Starting market data subscriptions...")
        await tick_stream.start()
        
        logger.info("=" * 80)
        logger.info("Streaming service started successfully. Beginning data collection...")
        logger.info(f"Subscribed symbols: {list(tick_stream.subscribed.keys())}")
        logger.info(f"Tick collection interval: 0.4 seconds (~2.5 ticks/second)")
        logger.info("=" * 80)
        
        while not shutdown_flag:
            iteration += 1
            try:
                # Get tick data
                ticks = tick_stream.get_ticks()
                
                if not ticks:
                    logger.warning("No tick data received in this iteration")
                    await asyncio.sleep(0.4)
                    continue
                
                # Process each symbol
                for sym, tick in ticks.items():
                    try:
                        # Update candles (will skip if price is invalid)
                        candles = candle_engine.update(tick)
                        micro = compute_microstructure(tick)
                        
                        tick_count += 1
                        
                        # Log periodic status (every 100 ticks)
                        if tick_count % 100 == 0:
                            logger.info(f"Processed {tick_count} ticks | Symbol: {sym} | Bid: {tick['bid']} | Ask: {tick['ask']} | Mid: {tick['mid']}")
                        
                        # Get latest candle for 1m timeframe (for chart display)
                        latest_candle = None
                        if sym in candles and "1m" in candles[sym]:
                            # Get the most recent candle bucket
                            candle_buckets = candles[sym]["1m"]
                            if candle_buckets:
                                latest_bucket = max(candle_buckets.keys())
                                latest_candle = candle_buckets[latest_bucket]
                        
                        # Normalize message format for frontend
                        message = {
                            "type": "tick",
                            "symbol": sym,
                            "tick": {
                                "bid": tick["bid"],
                                "ask": tick["ask"],
                                "mid": tick["mid"],
                                "spread": tick.get("spread", tick["ask"] - tick["bid"]),
                                "timestamp": tick.get("timestamp", time.time())
                            },
                            "candle": latest_candle if latest_candle else {},
                            "micro": micro
                        }
                        
                        await push(message)
                    except Exception as e:
                        logger.error(f"Error processing tick for {sym}: {e}", exc_info=True)
                
                # Log iteration summary every 50 iterations
                if iteration % 50 == 0:
                    logger.info(f"Iteration #{iteration} | Total ticks processed: {tick_count} | Active symbols: {len(ticks)}")
                
                await asyncio.sleep(0.4)   # ~2.5 ticks/second
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                shutdown_flag = True
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Wait before retrying
        
    except Exception as e:
        logger.critical(f"Fatal error in main execution: {e}", exc_info=True)
        raise
    finally:
        logger.info("=" * 80)
        logger.info("IBKR Streaming Service Shutting Down")
        logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total ticks processed: {tick_count}")
        logger.info("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
