# File: stock_market_game/app/api/endpoints/orderbook.py
from fastapi import APIRouter, HTTPException, Query
import json
import time  # ensure time is imported

from app.redis_client import redis_client
from app.database import SessionLocal
from app.models import PendingOrder

router = APIRouter()

def get_pending_orders(symbol: str, side: str):
    session = SessionLocal()
    try:
        orders = session.query(PendingOrder).filter(
            PendingOrder.symbol == symbol,
            PendingOrder.side == side
        ).all()
        orders_list = []
        for order in orders:
            orders_list.append({
                "order_id": order.order_id,
                "user_id": order.user_id,
                "symbol": order.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "order_type": order.order_type,
                "limit_price": order.limit_price,
                "timestamp": order.timestamp
            })
        return orders_list
    finally:
        session.close()

@router.get("/")
def get_orderbook(symbol: str = Query("HACK", description="Stock symbol (e.g., HACK)")):
    # Retrieve simulated orderbook from Redis.
    buy_data = redis_client.get(f"orderbook:buy:{symbol.upper()}")
    sell_data = redis_client.get(f"orderbook:sell:{symbol.upper()}")
    simulated_buy = []
    simulated_sell = []
    if buy_data:
        try:
            simulated_buy = json.loads(buy_data).get("orders", [])
        except Exception:
            simulated_buy = []
    if sell_data:
        try:
            simulated_sell = json.loads(sell_data).get("orders", [])
        except Exception:
            simulated_sell = []
    
    # Retrieve pending orders from the database.
    pending_buy = get_pending_orders(symbol.upper(), "buy")
    pending_sell = get_pending_orders(symbol.upper(), "sell")
    
    # Merge simulated orders with pending orders.
    merged_buy = simulated_buy + pending_buy
    merged_sell = simulated_sell + pending_sell

    # Sort orders: For pending orders, use 'limit_price' if 'price' is not available.
    merged_buy.sort(key=lambda x: x.get("price", x.get("limit_price", 0)), reverse=True)
    merged_sell.sort(key=lambda x: x.get("price", x.get("limit_price", 0)))
    
    return {
        "buy_orders": merged_buy,
        "sell_orders": merged_sell,
        "timestamp": int(time.time())
    }
