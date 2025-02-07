from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.order_matching import process_order

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
    executed_price: float = None
    quantity: float = None
    message: str = None

@router.post("/", response_model=OrderResponse)
def place_order(order: OrderRequest):
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
