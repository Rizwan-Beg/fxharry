"""Unit tests for ExecutionEngine."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from ai_core.execution.execution_engine import ExecutionEngine
from ai_core.execution.execution_config import ExecutionMode
from ai_core.execution.order_manager import OrderState
from ai_core.risk_manager.risk_manager import RiskManager


@pytest.fixture
def mock_risk_manager():
    """Create a mock risk manager."""
    risk_mgr = Mock(spec=RiskManager)
    
    # Mock position size calculation
    risk_mgr.calculate_position_size.return_value = {
        'quantity': 10000,
        'position_value': 11000,
        'risk_amount': 100,
        'risk_percent': 0.01,
        'position_size_percent': 0.011
    }
    
    # Mock risk assessment - approved
    risk_mgr.assess_trade_risk.return_value = {
        'approved': True,
        'risk_score': 0.3,
        'risk_level': 'LOW',
        'position_size_percent': 0.011,
        'warnings': []
    }
    
    return risk_mgr


@pytest.fixture
def mock_broker():
    """Create a mock broker service."""
    broker = AsyncMock()
    broker.place_order = AsyncMock(return_value={'order_id': 'BROKER-123'})
    return broker


@pytest.fixture
def execution_engine(mock_risk_manager):
    """Create execution engine for testing."""
    return ExecutionEngine(
        broker_service=None,  # No broker for paper trading tests
        risk_manager=mock_risk_manager
    )


class TestExecutionEngine:
    """Test suite for ExecutionEngine."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, execution_engine):
        """Test execution engine initializes correctly."""
        assert execution_engine.enabled is True
        assert execution_engine.execution_mode == ExecutionMode.PAPER_TRADING
        assert execution_engine.order_manager is not None
        assert execution_engine.position_tracker is not None
        assert execution_engine.circuit_breaker is not None
    
    @pytest.mark.asyncio
    async def test_signal_validation(self, execution_engine):
        """Test signal format validation."""
        # Valid signal
        valid_signal = {
            'symbol': 'EUR/USD',
            'action': 'LONG',
            'price': 1.1000
        }
        assert execution_engine._validate_signal(valid_signal) is True
        
        # Missing required field
        invalid_signal = {
            'symbol': 'EUR/USD',
            'action': 'LONG'
            # missing 'price'
        }
        assert execution_engine._validate_signal(invalid_signal) is False
        
        # Invalid action
        invalid_action = {
            'symbol': 'EUR/USD',
            'action': 'INVALID',
            'price': 1.1000
        }
        assert execution_engine._validate_signal(invalid_action) is False
    
    @pytest.mark.asyncio
    async def test_paper_trading_entry_signal(self, execution_engine):
        """Test processing LONG entry signal in paper trading mode."""
        signal = {
            'strategy_id': 'apex',
            'symbol': 'EUR/USD',
            'action': 'LONG',
            'price': 1.1000,
            'stop_loss': 1.0900,
            'take_profit': 1.1300,
            'reason': 'M5 SMA crossover',
            'timestamp': datetime.now().isoformat()
        }
        
        # Process signal
        with patch('ai_core.execution.execution_engine.SessionLocal') as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session
            
            trade_id = await execution_engine.process_signal(signal)
            
            # Verify trade was created
            assert trade_id is not None
            
            # Verify position was added
            assert execution_engine.position_tracker.has_position('EUR/USD')
            
            # Verify order was created and filled
            orders = execution_engine.order_manager.get_active_orders()
            assert len(orders) == 0  # Should be moved to completed after fill
    
    @pytest.mark.asyncio
    async def test_risk_rejection(self, execution_engine, mock_risk_manager):
        """Test signal rejection by risk manager."""
        # Configure risk manager to reject
        mock_risk_manager.assess_trade_risk.return_value = {
            'approved': False,
            'risk_score': 0.9,
            'risk_level': 'HIGH',
            'warnings': ['Position size exceeds maximum']
        }
        
        signal = {
            'symbol': 'EUR/USD',
            'action': 'LONG',
            'price': 1.1000,
            'stop_loss': 1.0900,
            'take_profit': 1.1300
        }
        
        with patch('ai_core.execution.execution_engine.SessionLocal') as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session
            
            trade_id = await execution_engine.process_signal(signal)
            
            # Verify trade was not created
            assert trade_id is None
            assert not execution_engine.position_tracker.has_position('EUR/USD')
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_blocks_execution(self, execution_engine):
        """Test that circuit breaker blocks execution when tripped."""
        # Trip the circuit breaker
        execution_engine.circuit_breaker.manual_trip("Test trip")
        
        signal = {
            'symbol': 'EUR/USD',
            'action': 'LONG',
            'price': 1.1000
        }
        
        trade_id = await execution_engine.process_signal(signal)
        
        # Verify trade was not executed
        assert trade_id is None
        assert not execution_engine.position_tracker.has_position('EUR/USD')
    
    @pytest.mark.asyncio
    async def test_exit_signal(self, execution_engine):
        """Test processing EXIT signal to close position."""
        # First, create a position
        entry_signal = {
            'symbol': 'EUR/USD',
            'action': 'LONG',
            'price': 1.1000,
            'stop_loss': 1.0900,
            'take_profit': 1.1300
        }
        
        with patch('ai_core.execution.execution_engine.SessionLocal') as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session
            
            await execution_engine.process_signal(entry_signal)
            
            # Verify position exists
            assert execution_engine.position_tracker.has_position('EUR/USD')
            
            # Now send exit signal
            exit_signal = {
                'symbol': 'EUR/USD',
                'action': 'EXIT',
                'price': 1.1100,
                'reason': 'Take profit hit'
            }
            
            await execution_engine.process_signal(exit_signal)
            
            # Verify position was closed
            assert not execution_engine.position_tracker.has_position('EUR/USD')
    
    @pytest.mark.asyncio
    async def test_position_limit(self, execution_engine):
        """Test that max concurrent positions limit is enforced."""
        from ai_core.execution import execution_config
        
        # Set low limit for testing
        original_limit = execution_config.MAX_CONCURRENT_POSITIONS
        execution_config.MAX_CONCURRENT_POSITIONS = 2
        
        try:
            with patch('ai_core.execution.execution_engine.SessionLocal') as mock_db:
                mock_session = Mock()
                mock_db.return_value = mock_session
                
                # Create first two positions
                for i in range(2):
                    signal = {
                        'symbol': f'SYMBOL{i}',
                        'action': 'LONG',
                        'price': 1.1000
                    }
                    await execution_engine.process_signal(signal)
                
                # Try to create third position
                signal = {
                    'symbol': 'SYMBOL3',
                    'action': 'LONG',
                    'price': 1.1000
                }
                trade_id = await execution_engine.process_signal(signal)
                
                # Should be rejected
                assert trade_id is None
                assert not execution_engine.position_tracker.has_position('SYMBOL3')
        
        finally:
            # Restore original limit
            execution_config.MAX_CONCURRENT_POSITIONS = original_limit
    
    @pytest.mark.asyncio
    async def test_emergency_stop(self, execution_engine):
        """Test emergency stop functionality."""
        # Activate emergency stop
        execution_engine.emergency_stop()
        
        # Verify circuit breaker is tripped
        assert execution_engine.circuit_breaker.is_tripped is True
        assert execution_engine.enabled is False
        
        # Try to process signal
        signal = {
            'symbol': 'EUR/USD',
            'action': 'LONG',
            'price': 1.1000
        }
        
        trade_id = await execution_engine.process_signal(signal)
        
        # Should be blocked
        assert trade_id is None
    
    def test_get_status(self, execution_engine):
        """Test getting execution engine status."""
        status = execution_engine.get_status()
        
        assert 'enabled' in status
        assert 'execution_mode' in status
        assert 'circuit_breaker' in status
        assert 'orders' in status
        assert 'positions' in status
        assert status['execution_mode'] == ExecutionMode.PAPER_TRADING.value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
