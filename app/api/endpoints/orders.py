from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional
from app.services.order_matching import process_order
from app.dependencies import get_db, verify_user
from app.models import PendingOrder
from app.schemas import PendingOrderResponse

router = APIRouter()

class OrderRequest(BaseModel):
    user_id: int
    symbol: str
    side: str = Field(..., pattern="^(buy|sell)$", description="Order side: buy or sell")
    quantity: float = Field(..., gt=0, description="Quantity of shares")
    order_type: str = Field("market", pattern="^(market|limit)$", description="Order type (market or limit)")
    limit_price: float = Field(None, description="Limit price, required for limit orders")

class OrderResponse(BaseModel):
    status: str
    order_id: str = None
    executed: bool = False
    executed_price: Optional[float] = None
    quantity: float = None
    message: str = None

@router.post("/", response_model=OrderResponse)
def place_order(order: OrderRequest, current_user = Depends(verify_user)):
    # Ensure the authenticated user's user_id matches the order's user_id.
    if current_user.user_id != order.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to place order for this account"
        )
    try:
        result = process_order(order.dict())
        return OrderResponse(
            status="success",
            order_id=result.get("order_id"),
            executed=result.get("executed"),
            executed_price=result.get("executed_price"),
            quantity=order.quantity,
            message=result.get("message")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pending", response_model=List[PendingOrderResponse])
def get_pending_limit_orders(
    user_id: int = Query(..., description="ID of the user to retrieve pending limit orders for"),
    current_user = Depends(verify_user),
    db: Session = Depends(get_db)
):
    # Ensure that the authenticated user matches the requested user_id.
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view pending orders for this account"
        )
    orders = db.query(PendingOrder).filter(
        PendingOrder.user_id == user_id,
        PendingOrder.order_type == "limit"
    ).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No pending limit orders found for this user.")
    return orders

@router.delete("/cancel", status_code=200)
def cancel_limit_order(
    order_id: str = Query(..., description="ID of the pending limit order to cancel"),
    user_id: int = Query(..., description="ID of the user canceling the order"),
    current_user = Depends(verify_user),
    db: Session = Depends(get_db)
):
    # Ensure that the authenticated user matches the provided user_id.
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel orders for this account"
        )
    # Retrieve the pending order and ensure it belongs to the user.
    order = db.query(PendingOrder).filter(
        PendingOrder.order_id == order_id,
        PendingOrder.user_id == user_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pending order not found or already executed/canceled.")

    # Delete the pending order.
    db.delete(order)
    db.commit()
    return {"message": f"Pending order {order_id} has been canceled."}
