import asyncio
import aiohttp
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for fetching and managing market data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        
    async def get_live_forex_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get live forex data for specified symbols"""
        # This is a simplified implementation
        # In production, you would integrate with your IBKR service
        # or another real-time data provider
        
        forex_data = {}
        
        for symbol in symbols:
            # Simulate live forex data
            base_rates = {
                'EURUSD': 1.0850,
                'GBPUSD': 1.2650,
                'XAUUSD': 2020.50,
                'USDJPY': 149.20,
                'USDCAD': 1.3520
            }
            
            base_rate = base_rates.get(symbol, 1.0000)
            
            # Add some realistic price movement
            change_percent = (random.random() - 0.5) * 0.002  # ±0.1% max change
            current_price = base_rate * (1 + change_percent)
            
            forex_data[symbol] = {
                'symbol': symbol,
                'bid': current_price - 0.0002,
                'ask': current_price + 0.0002,
                'last': current_price,
                'open': base_rate,
                'high': current_price + abs(change_percent) * base_rate,
                'low': current_price - abs(change_percent) * base_rate,
                'close': current_price,
                'volume': random.randint(100000, 1000000),
                'change': current_price - base_rate,
                'change_percent': change_percent * 100,
                'spread': 0.0004,
                'timestamp': datetime.now().isoformat()
            }
        
        return forex_data
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1H', 
                                 start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get historical forex data"""
        # In production, this would fetch from IBKR or another data provider
        # For now, generate sample historical data
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        base_rates = {
            'EURUSD': 1.0850,
            'GBPUSD': 1.2650,
            'XAUUSD': 2020.50,
            'USDJPY': 149.20,
            'USDCAD': 1.3520
        }
        
        base_rate = base_rates.get(symbol, 1.0000)
        historical_data = []
        
        current_date = start_date
        current_price = base_rate
        
        # Generate hourly data
        while current_date <= end_date:
            # Random price movement
            change = (random.random() - 0.5) * 0.01  # ±0.5% max change
            new_price = current_price * (1 + change)
            
            high = max(current_price, new_price) + random.random() * 0.001 * current_price
            low = min(current_price, new_price) - random.random() * 0.001 * current_price
            
            historical_data.append({
                'timestamp': current_date.isoformat(),
                'open': current_price,
                'high': high,
                'low': low,
                'close': new_price,
                'volume': random.randint(10000, 100000)
            })
            
            current_price = new_price
            current_date += timedelta(hours=1)
        
        return historical_data
    
    async def get_technical_indicators(self, symbol: str, timeframe: str = '1H') -> Dict[str, Any]:
        """Calculate technical indicators for a symbol"""
        # Get historical data
        historical_data = await self.get_historical_data(symbol, timeframe)
        
        if len(historical_data) < 50:
            return {}
        
        # Extract closing prices
        closes = [float(data['close']) for data in historical_data[-50:]]
        highs = [float(data['high']) for data in historical_data[-50:]]
        lows = [float(data['low']) for data in historical_data[-50:]]
        
        indicators = {}
        
        try:
            # Simple Moving Averages
            indicators['sma_20'] = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
            indicators['sma_50'] = sum(closes) / 50 if len(closes) >= 50 else None
            
            # RSI (Relative Strength Index)
            indicators['rsi'] = self._calculate_rsi(closes)
            
            # MACD
            macd_data = self._calculate_macd(closes)
            indicators.update(macd_data)
            
            # Bollinger Bands
            bb_data = self._calculate_bollinger_bands(closes)
            indicators.update(bb_data)
            
            # ATR (Average True Range)
            indicators['atr'] = self._calculate_atr(highs, lows, closes)
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
        
        return indicators
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """Calculate MACD"""
        if len(prices) < 26:
            return {'macd': 0, 'macd_signal': 0, 'macd_histogram': 0}
        
        # EMA calculation
        def ema(data, period):
            multiplier = 2 / (period + 1)
            ema_values = [data[0]]
            for price in data[1:]:
                ema_values.append((price * multiplier) + (ema_values[-1] * (1 - multiplier)))
            return ema_values
        
        ema_12 = ema(prices, 12)
        ema_26 = ema(prices, 26)
        
        macd_line = [ema_12[i] - ema_26[i] for i in range(len(ema_26))]
        signal_line = ema(macd_line, 9)
        
        histogram = [macd_line[i] - signal_line[i] for i in range(len(signal_line))]
        
        return {
            'macd': macd_line[-1],
            'macd_signal': signal_line[-1],
            'macd_histogram': histogram[-1]
        }
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            current_price = prices[-1]
            return {
                'bb_upper': current_price * 1.02,
                'bb_middle': current_price,
                'bb_lower': current_price * 0.98
            }
        
        sma = sum(prices[-period:]) / period
        
        # Standard deviation
        variance = sum([(price - sma) ** 2 for price in prices[-period:]]) / period
        std_dev = variance ** 0.5
        
        return {
            'bb_upper': sma + (2 * std_dev),
            'bb_middle': sma,
            'bb_lower': sma - (2 * std_dev)
        }
    
    def _calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(highs) < period + 1:
            return 0.01  # Default ATR
        
        true_ranges = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close_prev = abs(highs[i] - closes[i-1])
            low_close_prev = abs(lows[i] - closes[i-1])
            
            true_range = max(high_low, high_close_prev, low_close_prev)
            true_ranges.append(true_range)
        
        return sum(true_ranges[-period:]) / period