# File: stock_market_game/app/tasks/background_tasks.py
import threading
import time
import json
import uuid
from app.services.simulation import simulate_stock_data, simulate_trades, simulate_orderbook
from app.tasks.background_account_updates import start_account_update_task
from app.database import SessionLocal
from app.models import PendingOrder, Account, Position, Trade
from app.redis_client import redis_client

def execute_pending_order(order):
    session = SessionLocal()
    try:
        # Re-attach the order to the current session:
        order = session.merge(order)
        
        account = session.query(Account).filter(Account.user_id == order.user_id).first()
        if not account:
            return

        # Retrieve or create a position for the symbol.
        position = session.query(Position).filter(
            Position.user_id == order.user_id,
            Position.symbol == order.symbol
        ).first()
        if not position:
            position = Position(user_id=order.user_id, symbol=order.symbol, quantity=0)
            session.add(position)

        # Get current price from Redis.
        data = redis_client.get(order.symbol.upper())
        if not data:
            return
        current_price = json.loads(data).get("price")
        total_value = current_price * order.quantity

        if order.side == "buy":
            if account.cash < total_value:
                return  # insufficient funds
            account.cash -= total_value
            position.quantity += order.quantity
        elif order.side == "sell":
            if position.quantity < order.quantity:
                return  # insufficient shares
            account.cash += total_value
            position.quantity -= order.quantity
        else:
            return

        # Record the trade.
        trade_record = Trade(
            order_id=order.order_id,
            user_id=order.user_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=current_price,
            timestamp=int(time.time())
        )
        session.add(trade_record)

        # Remove the pending order as it is now executed.
        session.delete(order)
        session.commit()
        print(f"Executed pending order {order.order_id} at price {current_price}")
    except Exception as e:
        session.rollback()
        print(f"Error executing pending order: {e}")
    finally:
        session.close()

def check_pending_orders():
    session = SessionLocal()
    try:
        pending_orders = session.query(PendingOrder).all()
        for order in pending_orders:
            data = redis_client.get(order.symbol.upper())
            if not data:
                continue
            current_price = json.loads(data).get("price")
            if order.side == "buy" and current_price <= order.limit_price:
                execute_pending_order(order)
            elif order.side == "sell" and current_price >= order.limit_price:
                execute_pending_order(order)
    except Exception as e:
        print(f"Error checking pending orders: {e}")
    finally:
        session.close()

def run_pending_order_checker():
    while True:
        check_pending_orders()
        time.sleep(10)  # Check every 10 seconds; adjust as needed.

def start_pending_order_checker():
    thread = threading.Thread(target=run_pending_order_checker)
    thread.daemon = True
    thread.start()

def start_background_tasks():
    simulate_stock_data()
    simulate_trades()
    simulate_orderbook()
    start_account_update_task()
    start_pending_order_checker()  # Start checking for pending orders
