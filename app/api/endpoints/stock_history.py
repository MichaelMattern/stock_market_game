# File: stock_market_game/app/api/endpoints/stock_history.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas import StockData
from app.redis_client import redis_client
from app.database import SessionLocal
from app.models import StockHistory
from sqlalchemy import desc
import json
import time
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/{symbol}/history", response_model=List[StockData])
async def get_stock_history(
    symbol: str,
    timeframe: str = Query("5m", description="Timeframe: 1m, 5m, 15m, 30m, 1h"),
    limit: Optional[int] = Query(100, description="Maximum number of data points to return")
):
    """
    Get historical stock data for a specific symbol at various timeframes.
    
    This endpoint retrieves historical data from the database.
    Available timeframes: 1m, 5m, 15m, 30m, 1h
    """
    # Map timeframe strings to database values
    timeframe_map = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h"
    }
    
    if timeframe not in timeframe_map:
        raise HTTPException(status_code=400, detail=f"Invalid timeframe. Use one of: {', '.join(timeframe_map.keys())}")
    
    # Get data from database
    session = SessionLocal()
    try:
        history = session.query(StockHistory).filter(
            StockHistory.symbol == symbol.upper(),
            StockHistory.interval == timeframe_map[timeframe]
        ).order_by(desc(StockHistory.timestamp)).limit(limit).all()
        
        if not history:
            # If no historical data is available, check if the symbol exists
            current_data = redis_client.get(symbol.upper())
            if not current_data:
                raise HTTPException(status_code=404, detail=f"Stock data for {symbol} not available")
            else:
                raise HTTPException(status_code=404, detail=f"No historical data available for {symbol} at {timeframe} timeframe")
        
        # Convert to StockData objects
        return [
            StockData(
                symbol=h.symbol,
                price=h.price,
                volume=h.volume,
                volatility=h.volatility,
                timestamp=int(h.timestamp.timestamp())  # Convert datetime to Unix timestamp
            )
            for h in history
        ]
    finally:
        session.close() 