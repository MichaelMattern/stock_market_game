from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models import Trade
from app.schemas import TradeData
from app.dependencies import verify_admin, verify_user

router = APIRouter()

@router.get("/", include_in_schema=False, response_model=List[TradeData], dependencies=[Depends(verify_admin)])
def get_trade_history(symbol: str = Query("HACK", description="Stock ticker symbol (e.g., HACK)")):
    """
    Retrieves all historic trades for the specified stock symbol, sorted by timestamp.
    Only accessible by admin users.
    """
    session: Session = SessionLocal()
    try:
        trades = session.query(Trade).filter(Trade.symbol == symbol.upper()).order_by(Trade.timestamp).all()
        if not trades:
            raise HTTPException(status_code=404, detail=f"No trades found for symbol {symbol}")
        return trades
    finally:
        session.close()


# New endpoint: users can view their own trades
@router.get("/my", response_model=List[TradeData])
def get_my_trades(
    symbol: Optional[str] = Query(None, description="Optional stock ticker symbol to filter trades"),
    current_user = Depends(verify_user)
):
    """
    Retrieves trade history for the authenticated user's account.
    Optionally, filter by a specific stock symbol.
    """
    session: Session = SessionLocal()
    try:
        query = session.query(Trade).filter(Trade.user_id == current_user.user_id)
        if symbol:
            query = query.filter(Trade.symbol == symbol.upper())
        trades = query.order_by(Trade.timestamp).all()
        if not trades:
            raise HTTPException(status_code=404, detail="No trades found for your account.")
        return trades
    finally:
        session.close()

@router.get("/admin/user/{user_id}", include_in_schema=False, response_model=List[TradeData], dependencies=[Depends(verify_admin)])
def get_user_trades(
    user_id: int,
    symbol: Optional[str] = Query(None, description="Optional stock ticker symbol to filter trades")
):
    """
    Admin endpoint to get trades for a specific user.
    This endpoint is protected by an admin API key.
    """
    session: Session = SessionLocal()
    try:
        query = session.query(Trade).filter(Trade.user_id == user_id)
        if symbol:
            query = query.filter(Trade.symbol == symbol.upper())
        trades = query.order_by(Trade.timestamp).all()
        return trades
    finally:
        session.close()