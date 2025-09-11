import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import Trade, Strategy, AccountSnapshot
from database.database import SessionLocal
import numpy as np

logger = logging.getLogger(__name__)

class RiskManager:
    """Risk management service for trading operations"""
    
    def __init__(self):
        self.max_daily_loss = 0.02  # 2% max daily loss
        self.max_position_size = 0.05  # 5% max per position
        self.max_correlation_exposure = 0.15  # 15% max correlated exposure
        self.max_drawdown_limit = 0.20  # 20% max drawdown
        
    def assess_trade_risk(self, symbol: str, action: str, quantity: float, 
                         entry_price: float, account_value: float) -> Dict[str, Any]:
        """Assess risk for a potential trade"""
        position_value = quantity * entry_price
        position_size_percent = position_value / account_value
        
        risk_assessment = {
            'symbol': symbol,
            'position_value': position_value,
            'position_size_percent': position_size_percent,
            'risk_score': 0.0,
            'warnings': [],
            'approved': True
        }
        
        # Check position size
        if position_size_percent > self.max_position_size:
            risk_assessment['warnings'].append(
                f"Position size ({position_size_percent:.1%}) exceeds maximum ({self.max_position_size:.1%})"
            )
            risk_assessment['risk_score'] += 0.3
            risk_assessment['approved'] = False
        
        # Check daily loss limit
        daily_pnl = self._get_daily_pnl()
        if daily_pnl < -self.max_daily_loss * account_value:
            risk_assessment['warnings'].append(
                f"Daily loss limit reached ({daily_pnl:.2f})"
            )
            risk_assessment['risk_score'] += 0.4
            risk_assessment['approved'] = False
        
        # Check correlation exposure
        correlation_exposure = self._calculate_correlation_exposure(symbol, action, quantity)
        if correlation_exposure > self.max_correlation_exposure:
            risk_assessment['warnings'].append(
                f"Correlation exposure ({correlation_exposure:.1%}) exceeds limit"
            )
            risk_assessment['risk_score'] += 0.2
        
        # Check drawdown
        current_drawdown = self._calculate_current_drawdown()
        if current_drawdown > self.max_drawdown_limit:
            risk_assessment['warnings'].append(
                f"Drawdown ({current_drawdown:.1%}) exceeds limit ({self.max_drawdown_limit:.1%})"
            )
            risk_assessment['risk_score'] += 0.5
            risk_assessment['approved'] = False
        
        # Volatility adjustment
        volatility_risk = self._assess_volatility_risk(symbol)
        risk_assessment['risk_score'] += volatility_risk
        
        # Final risk classification
        if risk_assessment['risk_score'] < 0.3:
            risk_assessment['risk_level'] = 'LOW'
        elif risk_assessment['risk_score'] < 0.6:
            risk_assessment['risk_level'] = 'MEDIUM'
        else:
            risk_assessment['risk_level'] = 'HIGH'
            if risk_assessment['risk_score'] > 0.8:
                risk_assessment['approved'] = False
        
        return risk_assessment
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                               stop_loss: float, risk_percent: float = 0.01,
                               account_value: float = 100000) -> Dict[str, Any]:
        """Calculate optimal position size based on risk management"""
        if stop_loss == 0 or entry_price == stop_loss:
            return {'quantity': 0, 'error': 'Invalid stop loss'}
        
        # Risk per share/unit
        risk_per_unit = abs(entry_price - stop_loss)
        
        # Maximum risk amount
        max_risk_amount = account_value * risk_percent
        
        # Calculate position size
        position_size = max_risk_amount / risk_per_unit
        
        # Apply position size limits
        max_position_value = account_value * self.max_position_size
        max_quantity_by_size = max_position_value / entry_price
        
        final_quantity = min(position_size, max_quantity_by_size)
        
        return {
            'quantity': final_quantity,
            'position_value': final_quantity * entry_price,
            'risk_amount': final_quantity * risk_per_unit,
            'risk_percent': (final_quantity * risk_per_unit) / account_value,
            'position_size_percent': (final_quantity * entry_price) / account_value
        }
    
    def assess_portfolio_risk(self) -> Dict[str, Any]:
        """Assess overall portfolio risk"""
        db = SessionLocal()
        try:
            # Get open positions
            open_trades = db.query(Trade).filter(Trade.status == 'OPEN').all()
            
            total_exposure = 0
            symbol_exposures = {}
            currency_exposures = {}
            
            for trade in open_trades:
                exposure = trade.quantity * trade.entry_price
                total_exposure += exposure
                
                # Symbol exposure
                if trade.symbol not in symbol_exposures:
                    symbol_exposures[trade.symbol] = 0
                symbol_exposures[trade.symbol] += exposure
                
                # Currency exposure (simplified)
                base_currency = trade.symbol[:3] if len(trade.symbol) == 6 else 'USD'
                if base_currency not in currency_exposures:
                    currency_exposures[base_currency] = 0
                currency_exposures[base_currency] += exposure
            
            # Get latest account snapshot
            latest_snapshot = db.query(AccountSnapshot).order_by(
                AccountSnapshot.timestamp.desc()
            ).first()
            
            account_value = latest_snapshot.total_equity if latest_snapshot else 100000
            
            # Calculate risk metrics
            portfolio_risk = {
                'total_exposure': total_exposure,
                'exposure_ratio': total_exposure / account_value if account_value > 0 else 0,
                'open_positions': len(open_trades),
                'symbol_exposures': symbol_exposures,
                'currency_exposures': currency_exposures,
                'risk_level': 0.0,
                'warnings': []
            }
            
            # Risk level calculation
            if portfolio_risk['exposure_ratio'] > 0.8:
                portfolio_risk['risk_level'] = 0.9
                portfolio_risk['warnings'].append('Very high portfolio exposure')
            elif portfolio_risk['exposure_ratio'] > 0.5:
                portfolio_risk['risk_level'] = 0.6
                portfolio_risk['warnings'].append('High portfolio exposure')
            elif portfolio_risk['exposure_ratio'] > 0.3:
                portfolio_risk['risk_level'] = 0.4
            else:
                portfolio_risk['risk_level'] = 0.2
            
            # Check concentration risk
            max_symbol_exposure = max(symbol_exposures.values()) if symbol_exposures else 0
            if max_symbol_exposure / account_value > 0.1:  # 10% concentration limit
                portfolio_risk['warnings'].append('High concentration risk detected')
                portfolio_risk['risk_level'] += 0.2
            
            return portfolio_risk
            
        finally:
            db.close()
    
    def _get_daily_pnl(self) -> float:
        """Get today's PnL"""
        db = SessionLocal()
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_trades = db.query(Trade).filter(
                Trade.entry_time >= today,
                Trade.status.in_(['CLOSED', 'OPEN'])
            ).all()
            
            daily_pnl = sum(trade.pnl for trade in today_trades)
            return daily_pnl
            
        finally:
            db.close()
    
    def _calculate_correlation_exposure(self, symbol: str, action: str, quantity: float) -> float:
        """Calculate correlation exposure for currency pairs"""
        # Simplified correlation calculation
        # In production, you would use historical correlation matrices
        
        correlation_groups = {
            'EUR': ['EURUSD', 'EURJPY', 'EURGBP'],
            'GBP': ['GBPUSD', 'GBPJPY', 'EURGBP'],
            'USD': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD'],
            'JPY': ['USDJPY', 'EURJPY', 'GBPJPY'],
            'GOLD': ['XAUUSD']
        }
        
        # Find correlation group
        current_group = None
        for currency, pairs in correlation_groups.items():
            if symbol in pairs:
                current_group = pairs
                break
        
        if not current_group:
            return 0.1  # Default low correlation
        
        # Calculate existing exposure in correlation group
        db = SessionLocal()
        try:
            open_trades = db.query(Trade).filter(
                Trade.status == 'OPEN',
                Trade.symbol.in_(current_group)
            ).all()
            
            total_exposure = sum(trade.quantity * trade.entry_price for trade in open_trades)
            
            # Get account value (simplified)
            account_value = 100000  # Should get from account service
            
            return total_exposure / account_value if account_value > 0 else 0
            
        finally:
            db.close()
    
    def _calculate_current_drawdown(self) -> float:
        """Calculate current drawdown from peak equity"""
        db = SessionLocal()
        try:
            # Get account snapshots for the last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            snapshots = db.query(AccountSnapshot).filter(
                AccountSnapshot.timestamp >= thirty_days_ago
            ).order_by(AccountSnapshot.timestamp).all()
            
            if not snapshots:
                return 0.0
            
            equity_values = [snapshot.total_equity for snapshot in snapshots]
            peak_equity = max(equity_values)
            current_equity = equity_values[-1]
            
            drawdown = (peak_equity - current_equity) / peak_equity
            return max(0, drawdown)
            
        finally:
            db.close()
    
    def _assess_volatility_risk(self, symbol: str) -> float:
        """Assess volatility-based risk for symbol"""
        # Simplified volatility assessment
        # In production, you would calculate actual volatility metrics
        
        high_volatility_symbols = ['XAUUSD', 'GBPJPY', 'GBPUSD']
        medium_volatility_symbols = ['EURUSD', 'USDJPY', 'USDCAD']
        
        if symbol in high_volatility_symbols:
            return 0.2
        elif symbol in medium_volatility_symbols:
            return 0.1
        else:
            return 0.05
    
    def get_risk_limits(self) -> Dict[str, float]:
        """Get current risk limits"""
        return {
            'max_daily_loss_percent': self.max_daily_loss * 100,
            'max_position_size_percent': self.max_position_size * 100,
            'max_correlation_exposure_percent': self.max_correlation_exposure * 100,
            'max_drawdown_limit_percent': self.max_drawdown_limit * 100
        }
    
    def update_risk_limits(self, limits: Dict[str, float]) -> bool:
        """Update risk management limits"""
        try:
            if 'max_daily_loss_percent' in limits:
                self.max_daily_loss = limits['max_daily_loss_percent'] / 100
            if 'max_position_size_percent' in limits:
                self.max_position_size = limits['max_position_size_percent'] / 100
            if 'max_correlation_exposure_percent' in limits:
                self.max_correlation_exposure = limits['max_correlation_exposure_percent'] / 100
            if 'max_drawdown_limit_percent' in limits:
                self.max_drawdown_limit = limits['max_drawdown_limit_percent'] / 100
            
            logger.info("Risk limits updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating risk limits: {e}")
            return False