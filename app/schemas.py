# File: stock_market_game/app/schemas.py
from pydantic import BaseModel
from typing import Dict

class StockData(BaseModel):
    symbol: str
    price: float
    volume: float            # Changed from int to float
    volatility: float
    liquidity: float = None   # Optional, if you want to include it
    timestamp: int = None     # Optional

    # Optionally, if you want to ignore extra fields that may be present:
    class Config:
        extra = "ignore"

class AccountData(BaseModel):
    user_id: int
    password: str
    cash: float
    open_positions: Dict[str, float] = {}  # e.g., {"HACK": 10}
    profit_loss: float
    networth: float

    class Config:
        from_attributes = True  # For Pydantic v2; in v1 use orm_mode = True

class AccountCreate(BaseModel):
    user_id: int
    password: str

    class Config:
        from_attributes = True

class TradeData(BaseModel):
    order_id: str
    user_id: int
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: int

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    user_id: int
    cash: float
    profit_loss: float
    networth: float

    class Config:
        from_attributes = True  # or use orm_mode = True for Pydantic v1