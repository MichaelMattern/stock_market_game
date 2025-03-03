# File: stock_market_game/app/tasks/background_account_updates.py
import time
import threading
from app.database import SessionLocal
from app.models import Account
from app.api.endpoints.accounts import compute_networth

def update_account_values(interval: int = 10):
    """
    Periodically updates each account's profit_loss in the database.
    For this example, we define profit_loss as:
      profit_loss = networth - 10000.0
    (assuming a new account starts at 10000 cash)
    """
    while True:
        session = SessionLocal()
        try:
            accounts = session.query(Account).all()
            for account in accounts:
                net = compute_networth(account.cash, account.open_positions)
                # Here we assume the baseline networth for a new account is 10000.0.
                account.profit_loss = net - 10000.0
            session.commit()
        except Exception as e:
            session.rollback()
            print("Error updating account values:", e)
        finally:
            session.close()
        time.sleep(interval)

def start_account_update_task():
    thread = threading.Thread(target=update_account_values, daemon=True)
    thread.start()
