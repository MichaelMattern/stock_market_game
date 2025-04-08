# File: stock_market_game/app/api/endpoints/orderbook.py
from fastapi import APIRouter, HTTPException, Query
import json
import time  # ensure time is imported

from app.redis_client import redis_client
from app.database import SessionLocal
from app.models import PendingOrder

router = APIRouter()

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
            simulated_buy = [] # Default to empty list on error
    if sell_data:
        try:
            simulated_sell = json.loads(sell_data).get("orders", [])
        except Exception:
            simulated_sell = [] # Default to empty list on error

    # Retrieve pending orders from the database and format them.
    session = SessionLocal()
    try:
        pending_buy_db = session.query(PendingOrder).filter(
            PendingOrder.symbol == symbol.upper(),
            PendingOrder.side == "buy",
            PendingOrder.order_type == "limit"
        ).all()
        pending_sell_db = session.query(PendingOrder).filter(
            PendingOrder.symbol == symbol.upper(),
            PendingOrder.side == "sell",
            PendingOrder.order_type == "limit"
        ).all()

        # Transform pending orders to {price, volume} format
        formatted_pending_buy = [
            {"price": order.limit_price, "volume": order.quantity}
            for order in pending_buy_db if order.limit_price is not None
        ]
        formatted_pending_sell = [
            {"price": order.limit_price, "volume": order.quantity}
            for order in pending_sell_db if order.limit_price is not None
        ]
    finally:
        session.close()

    # Merge simulated orders with formatted pending orders.
    merged_buy = simulated_buy + formatted_pending_buy
    merged_sell = simulated_sell + formatted_pending_sell

    # Sort orders by price.
    # All entries now consistently have a 'price' key.
    merged_buy.sort(key=lambda x: x["price"], reverse=True)
    merged_sell.sort(key=lambda x: x["price"])

    return {
        "buy_orders": merged_buy,
        "sell_orders": merged_sell,
        "timestamp": int(time.time())
    }
