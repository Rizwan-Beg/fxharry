from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class OrderEvent(Base):
    """Audit trail for order lifecycle events."""
    __tablename__ = "order_events"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), index=True)
    event_type = Column(String(50))  # CREATED, SUBMITTED, FILLED, CANCELLED, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(JSON, nullable=True)
    broker_response = Column(JSON, nullable=True)
    order_state = Column(String(20), nullable=True)  # Order state at time of event
    notes = Column(Text, nullable=True)
