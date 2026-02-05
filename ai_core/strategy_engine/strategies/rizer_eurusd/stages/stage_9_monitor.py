"""
Stage 9: Trade Monitoring
Continuous re-evaluation for early exit conditions.
"""

from typing import Dict, Optional


class TradeMonitoring:
    """
    Stage 9: Trade Monitoring
    
    Re-evaluates open positions every candle for exit conditions:
    - VWAP invalidation
    - EMA structure break
    - Momentum decay (RSI reversal)
    
    Allows early exit before hitting stop loss or take profit.
    """
    
    def __init__(self):
        """Initialize trade monitoring."""
        self.position_state = {}
    
    def evaluate(self, position_side: Optional[str],
                 price: float, vwap: Optional[float],
                 ema_20: Optional[float], ema_50: Optional[float],
                 rsi: Optional[float],
                 entry_price: float = None) -> Dict:
        """
        Evaluate exit conditions for open position.
        
        Args:
            position_side: 'LONG' or 'SHORT'
            price: Current price
            vwap: Current VWAP
            ema_20: 20-period EMA
            ema_50: 50-period EMA
            rsi: RSI(14)
            entry_price: Entry price of position
            
        Returns:
            {
                'should_exit': bool,
                'exit_reason': str or None,
                'exit_conditions': dict
            }
        """
        if position_side is None:
            return {
                'should_exit': False,
                'exit_reason': None,
                'exit_conditions': {}
            }
        
        exit_conditions = {}
        exit_reasons = []
        
        # Track previous VWAP state
        position_key = f"{position_side}"
        if position_key not in self.position_state:
            self.position_state[position_key] = {
                'above_vwap': price > vwap if vwap else None,
                'ema_aligned': None
            }
        
        prev_state = self.position_state[position_key]
        
        # Check LONG position exits
        if position_side == 'LONG':
            # Exit 1: VWAP invalidation
            if vwap is not None:
                currently_above_vwap = price > vwap
                previously_above_vwap = prev_state.get('above_vwap', True)
                
                if previously_above_vwap and not currently_above_vwap:
                    exit_conditions['vwap_violation'] = True
                    exit_reasons.append('VWAP_VIOLATION')
                
                # Update state
                self.position_state[position_key]['above_vwap'] = currently_above_vwap
            
            # Exit 2: Structure break
            if ema_20 is not None and ema_50 is not None:
                if ema_20 < ema_50:
                    exit_conditions['structure_break'] = True
                    exit_reasons.append('STRUCTURE_BREAK')
            
            # Exit 3: Momentum exhaustion
            if rsi is not None and rsi > 70:
                exit_conditions['momentum_exhaustion'] = True
                exit_reasons.append('MOMENTUM_EXHAUSTION')
        
        # Check SHORT position exits
        elif position_side == 'SHORT':
            # Exit 1: VWAP invalidation
            if vwap is not None:
                currently_below_vwap = price < vwap
                previously_below_vwap = prev_state.get('above_vwap') == False if prev_state.get('above_vwap') is not None else True
                
                if previously_below_vwap and not currently_below_vwap:
                    exit_conditions['vwap_violation'] = True
                    exit_reasons.append('VWAP_VIOLATION')
                
                # Update state
                self.position_state[position_key]['above_vwap'] = not currently_below_vwap
            
            # Exit 2: Structure break
            if ema_20 is not None and ema_50 is not None:
                if ema_20 > ema_50:
                    exit_conditions['structure_break'] = True
                    exit_reasons.append('STRUCTURE_BREAK')
            
            # Exit 3: Momentum exhaustion
            if rsi is not None and rsi < 30:
                exit_conditions['momentum_exhaustion'] = True
                exit_reasons.append('MOMENTUM_EXHAUSTION')
        
        # Decision
        should_exit = len(exit_reasons) > 0
        exit_reason = exit_reasons[0] if exit_reasons else None
        
        return {
            'should_exit': should_exit,
            'exit_reason': exit_reason,
            'exit_conditions': exit_conditions
        }
    
    def reset_position_state(self, position_side: str):
        """Reset state for a position (call on exit)."""
        position_key = f"{position_side}"
        if position_key in self.position_state:
            del self.position_state[position_key]
