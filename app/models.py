# File: stock_market_game/app/models.py
from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, DateTime
from app.database import Base
from datetime import datetime

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    password = Column(String, nullable=False)
    cash = Column(Float, default=10000.0)
    open_positions = Column(JSON, default={})  # e.g. {"HACK": 10, "AAPL": 5}
    profit_loss = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)  # Flag to identify admin accounts

class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    quantity = Column(Integer, default=0)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    side = Column(String)  # "buy" or "sell"
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(Integer)

class PendingOrder(Base):
    __tablename__ = "pending_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)  # "buy" or "sell"
    quantity = Column(Float, nullable=False)
    order_type = Column(String, nullable=False)  # "market" or "limit"
    limit_price = Column(Float, nullable=True)
    timestamp = Column(Integer, nullable=False)

class StockHistory(Base):
    __tablename__ = "historical_stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    liquidity = Column(Float, nullable=True)
    interval = Column(String, nullable=False)  # Using interval instead of timeframe

