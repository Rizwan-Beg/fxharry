"""
VWAP (Volume Weighted Average Price) Indicator
Measures institutional participation and fair value.
"""

import numpy as np
from typing import Optional
from datetime import datetime, time
import pytz


class VWAPIndicator:
    """
    Volume Weighted Average Price indicator.
    
    VWAP = Σ(Price × Volume) / Σ(Volume)
    
    Resets at the start of each trading session.
    """
    
    def __init__(self, reset_time: time = time(0, 0), timezone: str = "UTC"):
        """
        Initialize VWAP indicator.
        
        Args:
            reset_time: Time to reset VWAP (default: midnight UTC)
            timezone: Timezone for reset time (default: "UTC")
        """
        self.reset_time = reset_time
        self.timezone = pytz.timezone(timezone)
        
        self.cumulative_pv = 0.0  # Price × Volume
        self.cumulative_volume = 0.0
        self.last_reset_date = None
    
    def update(self, price: float, volume: float, timestamp: datetime = None) -> Optional[float]:
        """
        Update VWAP with new price and volume.
        
        Args:
            price: Current price (typically (high + low + close) / 3) 
            volume: Volume for the period
            timestamp: Timestamp of the bar (for session resets)
            
        Returns:
            Current VWAP value or None if no volume
        """
        if timestamp is None:
            timestamp = datetime.now(pytz.UTC)
        
        # Check if we need to reset for new session
        self._check_reset(timestamp)
        
        # Update cumulative values
        self.cumulative_pv += price * volume
        self.cumulative_volume += volume
        
        if self.cumulative_volume == 0:
            return None
        
        return self.cumulative_pv / self.cumulative_volume
    
    def calculate_typical_price(self, high: float, low: float, close: float) -> float:
        """
        Calculate typical price for VWAP.
        
        Args:
            high: High price
            low: Low price
            close: Close price
            
        Returns:
            Typical price (HLC/3)
        """
        return (high + low + close) / 3.0
    
    def _check_reset(self, timestamp: datetime):
        """Check if we need to reset VWAP for a new session."""
        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            timestamp = pytz.UTC.localize(timestamp)
        else:
            timestamp = timestamp.astimezone(pytz.UTC)
        
        current_date = timestamp.date()
        
        # Reset on new date
        if self.last_reset_date is None or current_date > self.last_reset_date:
            self.cumulative_pv = 0.0
            self.cumulative_volume = 0.0
            self.last_reset_date = current_date
    
    def reset(self):
        """Manually reset VWAP."""
        self.cumulative_pv = 0.0
        self.cumulative_volume = 0.0
        self.last_reset_date = None
    
    def get_distance(self, current_price: float, vwap: float, atr: float) -> float:
        """
        Calculate distance from VWAP in ATR units.
        
        Args:
            current_price: Current market price
            vwap: Current VWAP value
            atr: Average True Range
            
        Returns:
            Distance in ATR units (positive if above, negative if below)
        """
        if atr == 0 or vwap is None:
            return 0.0
        
        return (current_price - vwap) / atr


class SessionVWAP:
    """
    VWAP that resets at specific session times (London, New York).
    """
    
    SESSIONS = {
        'london': time(8, 0),   # 08:00 UTC
        'new_york': time(13, 0),  # 13:00 UTC
    }
    
    def __init__(self, session: str = 'london'):
        """
        Initialize session-based VWAP.
        
        Args:
            session: Trading session ('london' or 'new_york')
        """
        if session.lower() not in self.SESSIONS:
            raise ValueError(f"Unknown session: {session}. Use 'london' or 'new_york'")
        
        reset_time = self.SESSIONS[session.lower()]
        self.vwap = VWAPIndicator(reset_time=reset_time, timezone="UTC")
        self.session = session.lower()
    
    def update(self, high: float, low: float, close: float, volume: float, 
               timestamp: datetime = None) -> Optional[float]:
        """
        Update VWAP with new bar data.
        
        Args:
            high: High price
            low: Low price
            close: Close price
            volume: Volume
            timestamp: Bar timestamp
            
        Returns:
            Current VWAP value
        """
        typical_price = self.vwap.calculate_typical_price(high, low, close)
        return self.vwap.update(typical_price, volume, timestamp)


def calculate_vwap(prices: np.ndarray, volumes: np.ndarray) -> Optional[float]:
    """
    Simple VWAP calculation from price and volume arrays.
    
    Args:
        prices: Array of prices (typically typical price: (H+L+C)/3)
        volumes: Array of volumes
        
    Returns:
        VWAP value or None if no volume
    """
    if len(prices) == 0 or len(volumes) == 0:
        return None
    
    if len(prices) != len(volumes):
        raise ValueError("Prices and volumes arrays must have same length")
    
    total_volume = np.sum(volumes)
    
    if total_volume == 0:
        return None
    
    pv = prices * volumes
    return float(np.sum(pv) / total_volume)
