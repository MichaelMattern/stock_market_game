# File: stock_market_game/app/api/endpoints/trades.py
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import Trade
from app.schemas import TradeData

router = APIRouter()

@router.get("/", response_model=List[TradeData])
def get_trade_history(symbol: str = Query("HACK", description="Stock ticker symbol (e.g., HACK)")):
    """
    Retrieves all historic trades for the specified stock symbol, sorted by timestamp.
    """
    session: Session = SessionLocal()
    try:
        trades = session.query(Trade).filter(Trade.symbol == symbol.upper()).order_by(Trade.timestamp).all()
        if not trades:
            raise HTTPException(status_code=404, detail=f"No trades found for symbol {symbol}")
        return trades
    finally:
        session.close()
