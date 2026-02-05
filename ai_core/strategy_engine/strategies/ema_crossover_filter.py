# ai_core/strategy_engine/strategies/ema_crossover_filter.py

import time

class EMACrossoverFilter:
    """
    Triple EMA Crossover Filter Strategy optimized for 5-minute timeframes.
    
    Uses 20, 50, and 100 period EMAs to generate high-probability signals.
    Signals are only generated when all three EMAs are properly aligned,
    reducing false signals and ensuring trend confirmation.
    
    BUY Signal: EMA20 > EMA50 > EMA100 (bullish alignment)
    SELL Signal: EMA20 < EMA50 < EMA100 (bearish alignment)
    """
    
    def __init__(self):
        # Track previous EMA values per symbol to detect crossovers
        self.prev_ema_values = {}
    
    def generate_signal(self, symbol, price, features):
        """
        Generate trading signals based on triple EMA alignment.
        
        Args:
            symbol: Trading symbol
            price: Current price
            features: Dict containing ema_20, ema_50, ema_100
            
        Returns:
            Signal dict or None
        """
        ema_20 = features.get("ema_20")
        ema_50 = features.get("ema_50")
        ema_100 = features.get("ema_100")
        
        # Ensure all EMAs are available
        if ema_20 is None or ema_50 is None or ema_100 is None:
            return None
        
        # Get previous values for crossover detection
        prev_values = self.prev_ema_values.get(symbol, {})
        prev_ema_20 = prev_values.get("ema_20")
        prev_ema_50 = prev_values.get("ema_50")
        
        # Store current values for next iteration
        self.prev_ema_values[symbol] = {
            "ema_20": ema_20,
            "ema_50": ema_50,
            "ema_100": ema_100
        }
        
        # Calculate EMA alignment strength (for confidence scoring)
        bullish_strength = self._calculate_alignment_strength(ema_20, ema_50, ema_100, "bullish")
        bearish_strength = self._calculate_alignment_strength(ema_20, ema_50, ema_100, "bearish")
        
        # BULLISH SIGNAL: EMA20 > EMA50 > EMA100
        if ema_20 > ema_50 > ema_100:
            # Additional filter: Check if EMA20 recently crossed above EMA50
            if prev_ema_20 is not None and prev_ema_50 is not None:
                crossed_up = prev_ema_20 <= prev_ema_50 and ema_20 > ema_50
                
                # Generate strong signal on fresh crossover
                if crossed_up:
                    return {
                        "symbol": symbol,
                        "signal": "BUY",
                        "reason": f"EMA20 crossed above EMA50 with bullish alignment (20: {ema_20:.2f} > 50: {ema_50:.2f} > 100: {ema_100:.2f})",
                        "confidence": min(0.85, 0.70 + bullish_strength),  # 0.70-0.85 range
                        "strategy_id": "EMA_CROSSOVER_FILTER",
                        "timestamp": int(time.time() * 1000),
                        "metadata": {
                            "ema_20": ema_20,
                            "ema_50": ema_50,
                            "ema_100": ema_100,
                            "crossover": True
                        }
                    }
                # Sustained bullish trend (all aligned but no recent cross)
                elif ema_20 > ema_50 * 1.001:  # At least 0.1% above to avoid noise
                    return {
                        "symbol": symbol,
                        "signal": "BUY",
                        "reason": f"Strong bullish EMA alignment (20: {ema_20:.2f} > 50: {ema_50:.2f} > 100: {ema_100:.2f})",
                        "confidence": min(0.78, 0.65 + bullish_strength),  # 0.65-0.78 range
                        "strategy_id": "EMA_CROSSOVER_FILTER",
                        "timestamp": int(time.time() * 1000),
                        "metadata": {
                            "ema_20": ema_20,
                            "ema_50": ema_50,
                            "ema_100": ema_100,
                            "crossover": False
                        }
                    }
        
        # BEARISH SIGNAL: EMA20 < EMA50 < EMA100
        elif ema_20 < ema_50 < ema_100:
            # Additional filter: Check if EMA20 recently crossed below EMA50
            if prev_ema_20 is not None and prev_ema_50 is not None:
                crossed_down = prev_ema_20 >= prev_ema_50 and ema_20 < ema_50
                
                # Generate strong signal on fresh crossover
                if crossed_down:
                    return {
                        "symbol": symbol,
                        "signal": "SELL",
                        "reason": f"EMA20 crossed below EMA50 with bearish alignment (20: {ema_20:.2f} < 50: {ema_50:.2f} < 100: {ema_100:.2f})",
                        "confidence": min(0.82, 0.68 + bearish_strength),  # 0.68-0.82 range
                        "strategy_id": "EMA_CROSSOVER_FILTER",
                        "timestamp": int(time.time() * 1000),
                        "metadata": {
                            "ema_20": ema_20,
                            "ema_50": ema_50,
                            "ema_100": ema_100,
                            "crossover": True
                        }
                    }
                # Sustained bearish trend (all aligned but no recent cross)
                elif ema_20 < ema_50 * 0.999:  # At least 0.1% below to avoid noise
                    return {
                        "symbol": symbol,
                        "signal": "SELL",
                        "reason": f"Strong bearish EMA alignment (20: {ema_20:.2f} < 50: {ema_50:.2f} < 100: {ema_100:.2f})",
                        "confidence": min(0.75, 0.62 + bearish_strength),  # 0.62-0.75 range
                        "strategy_id": "EMA_CROSSOVER_FILTER",
                        "timestamp": int(time.time() * 1000),
                        "metadata": {
                            "ema_20": ema_20,
                            "ema_50": ema_50,
                            "ema_100": ema_100,
                            "crossover": False
                        }
                    }
        
        # No signal when EMAs are not properly aligned (choppy market)
        return None
    
    def _calculate_alignment_strength(self, ema_20, ema_50, ema_100, direction):
        """
        Calculate how strong the EMA alignment is (0.0 to 0.15 bonus).
        Stronger separation = higher confidence.
        
        For 5-min timeframes, proper spacing indicates clearer trends.
        """
        if direction == "bullish":
            # Calculate percentage separation
            sep_20_50 = (ema_20 - ema_50) / ema_50 if ema_50 > 0 else 0
            sep_50_100 = (ema_50 - ema_100) / ema_100 if ema_100 > 0 else 0
            
            # Strong separation on 5-min = 0.2% to 1.0% typically
            strength = min(0.15, (sep_20_50 + sep_50_100) * 10)
            return max(0, strength)
        
        elif direction == "bearish":
            # Calculate percentage separation (negative for bearish)
            sep_20_50 = (ema_50 - ema_20) / ema_50 if ema_50 > 0 else 0
            sep_50_100 = (ema_100 - ema_50) / ema_100 if ema_100 > 0 else 0
            
            # Strong separation on 5-min = 0.2% to 1.0% typically
            strength = min(0.15, (sep_20_50 + sep_50_100) * 10)
            return max(0, strength)
        
        return 0
