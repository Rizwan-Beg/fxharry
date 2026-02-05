"""
Stage 8: Risk Management
ATR-based position sizing and stop loss / take profit calculation.
"""

from typing import Dict, Optional


class RiskManagement:
    """
    Stage 8: Risk Management
    
    Calculates position size, stop loss, and take profit based on:
    - ATR(14)
    - Account equity
    - Risk per trade
    - Volatility scaling
    
    Rules:
    - stop_loss = 1.2 × ATR
    - take_profit = 2.0 × stop_loss
    - position_size scaled to risk 1% of equity
    - Reduce size in high volatility
    """
    
    def __init__(self, atr_stop_multiplier: float = 1.2,
                 risk_reward_ratio: float = 2.0,
                 risk_per_trade_percent: float = 0.01,
                 high_volatility_threshold: float = 1.5,
                 high_volatility_size_reduction: float = 0.7):
        """
        Initialize risk management.
        
        Args:
            atr_stop_multiplier: Multiplier for ATR to set stop loss
            risk_reward_ratio: Take profit / stop loss ratio
            risk_per_trade_percent: Percentage of equity to risk per trade
            high_volatility_threshold: ATR threshold for high volatility
            high_volatility_size_reduction: Size reduction in high volatility
        """
        self.atr_stop_multiplier = atr_stop_multiplier
        self.risk_reward_ratio = risk_reward_ratio
        self.risk_per_trade_percent = risk_per_trade_percent
        self.high_volatility_threshold = high_volatility_threshold
        self.high_volatility_size_reduction = high_volatility_size_reduction
        
        # Track recent ATR for volatility comparison
        self.recent_atr_values = []
        self.max_atr_history = 50
    
    def evaluate(self, atr: float, account_equity: float, 
                 signal: Optional[str] = None,
                 current_price: float = 1.0) -> Dict:
        """
        Calculate risk parameters for trade.
        
        Args:
            atr: ATR(14) value
            account_equity: Current account equity
            signal: Trading signal ('LONG', 'SHORT', or None)
            current_price: Current market price
            
        Returns:
            {
                'stop_loss_pips': float,
                'take_profit_pips': float,
                'position_size': float,
                'risk_amount': float,
                'reward_amount': float,
                'volatility_adjusted': bool
            }
        """
        if signal is None or atr is None or atr == 0:
            return {
                'stop_loss_pips': 0.0,
                'take_profit_pips': 0.0,
                'position_size': 0.0,
                'risk_amount': 0.0,
                'reward_amount': 0.0,
                'volatility_adjusted': False
            }
        
        # Update ATR history
        self.recent_atr_values.append(atr)
        if len(self.recent_atr_values) > self.max_atr_history:
            self.recent_atr_values.pop(0)
        
        # Calculate stop loss in pips
        stop_loss_pips = atr * self.atr_stop_multiplier
        
        # Calculate take profit in pips
        take_profit_pips = stop_loss_pips * self.risk_reward_ratio
        
        # Calculate risk amount
        risk_amount = account_equity * self.risk_per_trade_percent
        
        # Calculate base position size
        # position_size = risk_amount / stop_loss_pips
        # For forex: position_size in lots = (risk_amount / stop_loss_pips) / pip_value
        # Simplified for EUR/USD where pip value ≈ 10 per lot per pip
        pip_value_per_lot = 10.0
        position_size = risk_amount / (stop_loss_pips * pip_value_per_lot)
        
        # Volatility adjustment
        volatility_adjusted = False
        if len(self.recent_atr_values) >= 20:
            avg_atr = sum(self.recent_atr_values[-20:]) / 20
            
            if atr > avg_atr * self.high_volatility_threshold:
                # High volatility - reduce position size
                position_size *= self.high_volatility_size_reduction
                volatility_adjusted = True
        
        # Calculate expected reward
        reward_amount = position_size * take_profit_pips * pip_value_per_lot
        
        return {
            'stop_loss_pips': float(stop_loss_pips),
            'take_profit_pips': float(take_profit_pips),
            'position_size': float(position_size),
            'risk_amount': float(risk_amount),
            'reward_amount': float(reward_amount),
            'volatility_adjusted': volatility_adjusted,
            'atr_value': float(atr)
        }
