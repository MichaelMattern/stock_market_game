# File: stock_market_game/app/services/order_matching.py
import json
import uuid
import time
from app.redis_client import redis_client
from app.database import SessionLocal
from app.models import Account, Position, Trade, PendingOrder  # Ensure PendingOrder is imported

def process_order(order: dict) -> dict:
    """
    Process an order by matching it against the current simulated orderbook,
    updating the user's account and positions, and recording the trade.
    If a limit order does not meet the execution criteria, store it as pending.
    """
    symbol = order.get("symbol").upper()
    side = order.get("side").lower()
    quantity = order.get("quantity")
    order_type = order.get("order_type", "market").lower()
    limit_price = order.get("limit_price")
    
    # Retrieve the simulated orderbook from Redis (separate keys for buy and sell orders)
    buy_data = redis_client.get(f"orderbook:buy:{symbol}")
    sell_data = redis_client.get(f"orderbook:sell:{symbol}")
    
    bids = []
    asks = []
    if buy_data:
        try:
            ob_buy = json.loads(buy_data)
            bids = ob_buy.get("orders", [])
        except Exception:
            pass
    if sell_data:
        try:
            ob_sell = json.loads(sell_data)
            asks = ob_sell.get("orders", [])
        except Exception:
            pass

    executed = False
    executed_price = None
    message = ""
    
    if order_type == "market":
        if side == "buy":
            if asks:
                best_ask = sorted(asks, key=lambda x: x["price"])[0]
                executed_price = best_ask["price"]
                executed = True
            else:
                message = "No ask orders available for execution."
        elif side == "sell":
            if bids:
                best_bid = sorted(bids, key=lambda x: x["price"], reverse=True)[0]
                executed_price = best_bid["price"]
                executed = True
            else:
                message = "No bid orders available for execution."
        else:
            message = "Invalid order side."
    elif order_type == "limit":
        if limit_price is None:
            message = "Limit price must be provided for limit orders."
        else:
            if side == "buy":
                if asks:
                    best_ask = sorted(asks, key=lambda x: x["price"])[0]
                    if best_ask["price"] <= limit_price:
                        executed_price = best_ask["price"]
                        executed = True
                    else:
                        message = f"Best ask price {best_ask['price']} exceeds limit {limit_price}; order pending."
                else:
                    message = "No ask orders available for limit execution."
            elif side == "sell":
                if bids:
                    best_bid = sorted(bids, key=lambda x: x["price"], reverse=True)[0]
                    if best_bid["price"] >= limit_price:
                        executed_price = best_bid["price"]
                        executed = True
                    else:
                        message = f"Best bid price {best_bid['price']} is below limit {limit_price}; order pending."
                else:
                    message = "No bid orders available for limit execution."
            else:
                message = "Invalid order side."
    else:
        message = "Unsupported order type."
    
    # Generate a unique order ID.
    order_id = str(uuid.uuid4())
    
    result = {
        "order_id": order_id,
        "executed": executed,
        "executed_price": executed_price,
        "message": message if not executed else "Order executed successfully."
    }
    
    # If the order is executed, update the account and record the trade.
    if executed:
        session = SessionLocal()
        try:
            account = session.query(Account).filter(Account.user_id == order.get("user_id")).first()
            if not account:
                raise Exception("Account not found for user.")
            # Retrieve or create a position for this symbol.
            position = session.query(Position).filter(
                Position.user_id == order.get("user_id"),
                Position.symbol == symbol
            ).first()
            if not position:
                position = Position(user_id=order.get("user_id"), symbol=symbol, quantity=0)
                session.add(position)
            
            # Round values before calculation and update
            rounded_executed_price = round(executed_price, 2)
            rounded_quantity = round(quantity, 2)
            total_value = round(rounded_executed_price * rounded_quantity, 2)

            if side == "buy":
                if account.cash < total_value:
                    raise Exception("Insufficient funds.")
                account.cash -= total_value
                # Round cash itself after update to ensure precision
                account.cash = round(account.cash, 2)
                position.quantity += rounded_quantity
            elif side == "sell":
                if position.quantity < rounded_quantity: # Compare with rounded quantity
                    raise Exception("Insufficient shares to sell.")
                account.cash += total_value
                # Round cash itself after update to ensure precision
                account.cash = round(account.cash, 2)
                position.quantity -= rounded_quantity
            else:
                raise Exception("Invalid order side during account update.")
            
            # Record the trade with rounded values.
            trade_record = Trade(
                order_id=order_id,
                user_id=order.get("user_id"),
                symbol=symbol,
                side=side,
                quantity=rounded_quantity, # Use rounded quantity
                price=rounded_executed_price, # Use rounded price
                timestamp=int(time.time())
            )
            session.add(trade_record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    # For limit orders that did not execute, store them as pending.
    elif order_type == "limit":
        session = SessionLocal()
        try:
            from app.models import PendingOrder  # Already imported at the top if needed.
            # Round values before saving pending order
            rounded_quantity = round(quantity, 2)
            # Ensure limit_price is not None before rounding
            rounded_limit_price = round(limit_price, 2) if limit_price is not None else None

            pending = PendingOrder(
                order_id=order_id,
                user_id=order.get("user_id"),
                symbol=symbol,
                side=side,
                quantity=rounded_quantity, # Use rounded quantity
                order_type=order_type,
                limit_price=rounded_limit_price, # Use rounded limit price
                timestamp=int(time.time())
            )
            session.add(pending)
            session.commit()
            result["message"] += " Order stored as pending."
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    return result
