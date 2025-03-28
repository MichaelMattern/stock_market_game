from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Trade
from app.schemas import TradeResponse, TradeStatsResponse
from app.dependencies import verify_admin
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/recent", response_model=List[TradeResponse], dependencies=[Depends(verify_admin)])
def get_recent_trades(
    limit: int = Query(10, description="Number of trades to return"),
    db: Session = Depends(get_db)
):
    """Get recent trades for the admin dashboard."""
    try:
        trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=TradeStatsResponse, dependencies=[Depends(verify_admin)])
def get_trade_stats(db: Session = Depends(get_db)):
    """Get trade statistics for the admin dashboard."""
    try:
        # Get total trades
        total_trades = db.query(Trade).count()
        
        # Get yesterday's date
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Get trades from today and yesterday
        today_trades = db.query(Trade).filter(
            Trade.timestamp >= yesterday
        ).count()
        
        # Calculate percentage change
        change = ((today_trades / total_trades) * 100) if total_trades > 0 else 0
        
        # Calculate total volume
        total_volume = db.query(Trade).with_entities(
            db.func.sum(Trade.price * Trade.quantity).label('total_volume')
        ).scalar() or 0
        
        # Calculate yesterday's volume
        yesterday_volume = db.query(Trade).filter(
            Trade.timestamp >= yesterday
        ).with_entities(
            db.func.sum(Trade.price * Trade.quantity).label('yesterday_volume')
        ).scalar() or 0
        
        # Calculate volume change
        volume_change = ((yesterday_volume / total_volume) * 100) if total_volume > 0 else 0
        
        return {
            "total": total_trades,
            "change": round(change, 2),
            "volume": total_volume,
            "volumeChange": round(volume_change, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 