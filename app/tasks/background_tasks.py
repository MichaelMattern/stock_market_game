# File: stock_market_game/app/tasks/background_tasks.py
from app.services.simulation import simulate_stock_data, simulate_trades, simulate_orderbook
from app.tasks.background_account_updates import start_account_update_task

def start_background_tasks():
    simulate_stock_data()
    simulate_trades()
    simulate_orderbook()
    start_account_update_task()
