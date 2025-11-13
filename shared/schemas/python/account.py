from pydantic import BaseModel
from typing import List


class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    market_value: float


class AccountSummary(BaseModel):
    status: str
    timestamp: str
    broker: str
    total_equity: float
    available_funds: float
    buying_power: float
    positions: List[Position] = []