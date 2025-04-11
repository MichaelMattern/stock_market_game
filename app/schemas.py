# File: stock_market_game/app/schemas.py
from pydantic import BaseModel
from typing import Dict, Optional

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
    is_admin: bool = False

    class Config:
        from_attributes = True  # For Pydantic v2; in v1 use orm_mode = True

class AccountCreate(BaseModel):
    user_id: int
    password: str
    initial_cash: float = 10000.0

    class Config:
        from_attributes = True

class AdminAccountCreate(BaseModel):
    user_id: int
    password: str
    is_admin: bool = True
    initial_cash: float = 10000.0

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
    networth: float     # Total net worth (cash + market_value)

    class Config:
        from_attributes = True

class PendingOrderResponse(BaseModel):
    order_id: str
    user_id: int
    symbol: str
    side: str
    quantity: float
    order_type: str
    limit_price: float = None
    timestamp: int

    class Config:
        from_attributes = True

class AdminLeaderboardEntry(BaseModel):
    user_id: int
    cash: float
    profit_loss: float  # Realized P/L
    market_value: float # Current market value of open positions
    networth: float     # Total net worth (cash + market_value)

    class Config:
        from_attributes = True

# Admin verification schema
class AdminVerify(BaseModel):
    admin_id: int