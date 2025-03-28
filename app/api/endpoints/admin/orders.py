from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import PendingOrder
from app.schemas import PendingOrderResponse, OrderStatsResponse
from app.dependencies import verify_admin
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/pending", response_model=List[PendingOrderResponse], dependencies=[Depends(verify_admin)])
def get_all_pending_orders(
    symbol: Optional[str] = Query(None, description="Optional stock symbol to filter orders"),
    user_id: Optional[int] = Query(None, description="Optional user ID to filter orders"),
    side: Optional[str] = Query(None, description="Optional order side (buy/sell) to filter orders"),
    order_type: Optional[str] = Query(None, description="Optional order type (market/limit) to filter orders"),
    limit: Optional[int] = Query(None, description="Maximum number of orders to return"),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to get all pending orders with optional filtering.
    This endpoint is protected by an admin API key.
    """
    try:
        query = db.query(PendingOrder)
        
        if symbol:
            query = query.filter(PendingOrder.symbol == symbol.upper())
        if user_id:
            query = query.filter(PendingOrder.user_id == user_id)
        if side:
            query = query.filter(PendingOrder.side == side.lower())
        if order_type:
            query = query.filter(PendingOrder.order_type == order_type.lower())
            
        query = query.order_by(PendingOrder.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
            
        orders = query.all()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=OrderStatsResponse, dependencies=[Depends(verify_admin)])
def get_order_stats(db: Session = Depends(get_db)):
    """Get order statistics for the admin dashboard."""
    try:
        # Get total pending orders
        total_orders = db.query(PendingOrder).count()
        
        # Get yesterday's date
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Get orders created today and yesterday
        today_orders = db.query(PendingOrder).filter(
            PendingOrder.timestamp >= yesterday
        ).count()
        
        # Calculate percentage change
        change = ((today_orders / total_orders) * 100) if total_orders > 0 else 0
        
        return {
            "pending": total_orders,
            "change": round(change, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cancel", dependencies=[Depends(verify_admin)])
def cancel_order_admin(
    order_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Admin endpoint to cancel any order."""
    try:
        # Find the order
        order = db.query(PendingOrder).filter(
            PendingOrder.order_id == order_id,
            PendingOrder.user_id == user_id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Delete the order
        db.delete(order)
        db.commit()
        
        return {"message": "Order cancelled successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 