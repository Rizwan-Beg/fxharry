"""Configuration for the execution engine."""

from enum import Enum


class ExecutionMode(Enum):
    """Execution mode types."""
    PAPER_TRADING = "PAPER_TRADING"  # Simulate trades without real execution
    LIVE_TRADING = "LIVE_TRADING"    # Execute real trades with real capital


# ============================================================================
# EXECUTION MODE - CRITICAL SETTING
# ============================================================================
# By default, the system starts in PAPER_TRADING mode for safety.
# CRITICAL: Set to LIVE_TRADING to send orders to IBKR TWS (Paper or Live).
# If set to PAPER_TRADING, orders are ONLY simulated internally and NOT sent to IBKR.
# To trade on IBKR Paper Account (Port 7497), this MUST be LIVE_TRADING.
EXECUTION_MODE = ExecutionMode.LIVE_TRADING

# ============================================================================
# CIRCUIT BREAKER SETTINGS
# ============================================================================
# Automatically halt trading when adverse conditions are detected
ENABLE_CIRCUIT_BREAKER = True

# Daily loss threshold to trigger circuit breaker (e.g., -0.01 = -1%)
CIRCUIT_BREAKER_LOSS_THRESHOLD = -0.01

# Number of consecutive losing trades before circuit breaker activates
CIRCUIT_BREAKER_CONSECUTIVE_LOSSES = 3

# ============================================================================
# RISK CONTROLS
# ============================================================================
# Manual approval required for trades with risk score above this threshold
MANUAL_APPROVAL_RISK_THRESHOLD = 0.7

# Maximum number of orders that can be placed per minute (throttling)
MAX_ORDERS_PER_MINUTE = 5

# ============================================================================
# EMERGENCY CONTROLS
# ============================================================================
# Enable kill switch feature (emergency stop for all trading)
ENABLE_KILL_SWITCH = True

# ============================================================================
# ORDER EXECUTION SETTINGS
# ============================================================================
# Maximum time to wait for order confirmation from broker (seconds)
ORDER_TIMEOUT_SECONDS = 30

# Number of retry attempts for failed orders
MAX_ORDER_RETRIES = 3

# Delay between retry attempts (seconds)
RETRY_DELAY_SECONDS = 2

# ============================================================================
# POSITION MANAGEMENT
# ============================================================================
# Maximum number of concurrent open positions
MAX_CONCURRENT_POSITIONS = 5

# Enable automatic position closure at end of trading day
ENABLE_EOD_POSITION_CLOSURE = False

# ============================================================================
# LOGGING & MONITORING
# ============================================================================
# Log all order events to database
ENABLE_ORDER_AUDIT_TRAIL = True

# Send alerts for rejected orders
ENABLE_REJECTION_ALERTS = True

# Log execution latency metrics
ENABLE_LATENCY_TRACKING = True


def get_config_summary():
    """Get a human-readable summary of current configuration."""
    return {
        "execution_mode": EXECUTION_MODE.value,
        "circuit_breaker_enabled": ENABLE_CIRCUIT_BREAKER,
        "circuit_breaker_loss_threshold": f"{CIRCUIT_BREAKER_LOSS_THRESHOLD * 100}%",
        "circuit_breaker_consecutive_losses": CIRCUIT_BREAKER_CONSECUTIVE_LOSSES,
        "manual_approval_threshold": MANUAL_APPROVAL_RISK_THRESHOLD,
        "max_orders_per_minute": MAX_ORDERS_PER_MINUTE,
        "kill_switch_enabled": ENABLE_KILL_SWITCH,
        "max_concurrent_positions": MAX_CONCURRENT_POSITIONS,
    }
