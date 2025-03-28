# File: stock_market_game/app/services/simulation.py
import time
import json
import numpy as np
import threading
from app.redis_client import redis_client
from app.database import SessionLocal
from app.models import StockHistory
from sqlalchemy.orm import Session
from datetime import datetime

# Maximum number of historical data points to keep per timeframe
MAX_HISTORY_POINTS = 1000

def store_historical_data(session: Session, symbol: str, stock_data: dict, timeframe: str):
    """
    Store historical data in the database.
    """
    try:
        print(f"Storing historical data: {symbol}, timeframe: {timeframe}, price: {stock_data['price']}")
        
        # Convert numpy types to standard Python types
        price = float(stock_data["price"])
        volume = float(stock_data["volume"])
        volatility = float(stock_data["volatility"])
        liquidity = float(stock_data.get("liquidity", 0))
        
        # Convert Unix timestamp to datetime
        timestamp = datetime.fromtimestamp(stock_data["timestamp"])
        
        history = StockHistory(
            symbol=symbol,
            price=price,
            volume=volume,
            volatility=volatility,
            timestamp=timestamp,  # Using datetime object now
            liquidity=liquidity,
            interval=timeframe  # Using interval instead of timeframe
        )
        session.add(history)
        session.commit()
        print(f"Successfully stored historical data for {symbol}")
    except Exception as e:
        print(f"Error storing historical data: {e}")
        session.rollback()

def run_simulation(symbol, params, dt=1/252, sleep_time=5, gamma=1e-4):
    """
    Simulates market dynamics for a given stock symbol, incorporating order flow feedback.
    Now also stores historical data in both Redis and the database.
    """
    # Initial state
    price = params["S0"]
    volatility = params["sigma0"]
    mu = params["mu"]
    base_volume = params["base_volume"]
    base_liquidity = params["base_liquidity"]

    while True:
        # --- Incorporate Order Flow Feedback ---
        imbalance_key = f"order_imbalance:{symbol}"
        imbalance_val = redis_client.get(imbalance_key)
        try:
            imbalance = float(imbalance_val) if imbalance_val is not None else 0.0
        except Exception:
            imbalance = 0.0
        # Reset imbalance after reading
        redis_client.set(imbalance_key, 0)
        effective_mu = mu + gamma * imbalance

        # --- Update Volatility (Ornstein–Uhlenbeck process) ---
        kappa = 0.1
        theta = params["sigma0"]
        xi = 0.05
        epsilon_vol = np.random.normal(0, 1)
        volatility = max(volatility + kappa * (theta - volatility) * dt + xi * np.sqrt(dt) * epsilon_vol, 0.001)

        # --- Update Price Using GBM ---
        epsilon_price = np.random.normal(0, 1)
        price = price * np.exp((effective_mu - 0.5 * volatility ** 2) * dt + volatility * np.sqrt(dt) * epsilon_price)

        # --- Simulate Volume ---
        sigma_volume = 0.1 * base_volume + 0.5 * volatility * base_volume
        volume = int(np.random.lognormal(mean=np.log(base_volume), sigma=sigma_volume / base_volume))

        # --- Simulate Liquidity ---
        liquidity = base_liquidity * (base_volume / volume) * (params["sigma0"] / volatility)

        # --- Build Market Data ---
        current_time = int(time.time())
        stock_data = {
            "symbol": symbol,
            "price": price,
            "volatility": volatility,
            "volume": volume,
            "liquidity": liquidity,
            "timestamp": current_time
        }
        
        # Store the current stock data in Redis under key "HACK"
        redis_client.set(symbol, json.dumps(stock_data))
        
        # Store historical data point in Redis and database
        stock_data_json = json.dumps(stock_data)
        
        # Create a database session
        session = SessionLocal()
        try:
            # Add to historical data for all timeframes
            # 1-minute data
            redis_client.zadd(f"history:1m:{symbol}", {stock_data_json: current_time})
            redis_client.zremrangebyrank(f"history:1m:{symbol}", 0, -MAX_HISTORY_POINTS-1)
            store_historical_data(session, symbol, stock_data, "1m")
            
            # Store in 5-minute history if it aligns with 5-minute intervals
            if current_time % 300 < sleep_time:
                redis_client.zadd(f"history:5m:{symbol}", {stock_data_json: current_time})
                redis_client.zremrangebyrank(f"history:5m:{symbol}", 0, -MAX_HISTORY_POINTS-1)
                store_historical_data(session, symbol, stock_data, "5m")
            
            # Store in 15-minute history if it aligns with 15-minute intervals
            if current_time % 900 < sleep_time:
                redis_client.zadd(f"history:15m:{symbol}", {stock_data_json: current_time})
                redis_client.zremrangebyrank(f"history:15m:{symbol}", 0, -MAX_HISTORY_POINTS-1)
                store_historical_data(session, symbol, stock_data, "15m")
            
            # Store in 30-minute history if it aligns with 30-minute intervals
            if current_time % 1800 < sleep_time:
                redis_client.zadd(f"history:30m:{symbol}", {stock_data_json: current_time})
                redis_client.zremrangebyrank(f"history:30m:{symbol}", 0, -MAX_HISTORY_POINTS-1)
                store_historical_data(session, symbol, stock_data, "30m")
            
            # Store in 1-hour history if it aligns with hourly intervals
            if current_time % 3600 < sleep_time:
                redis_client.zadd(f"history:1h:{symbol}", {stock_data_json: current_time})
                redis_client.zremrangebyrank(f"history:1h:{symbol}", 0, -MAX_HISTORY_POINTS-1)
                store_historical_data(session, symbol, stock_data, "1h")
        finally:
            session.close()
            
        time.sleep(sleep_time)

def run_trade_simulation(symbol, sleep_time=3):
    """
    Simulates trade events for a given stock symbol.
    """
    while True:
        data = redis_client.get(symbol)
        if data:
            try:
                stock = json.loads(data)
                current_price = stock.get("price", 100)
            except Exception:
                current_price = 100
            side = np.random.choice(["buy", "sell"])
            quantity = int(np.random.randint(1, 10))
            deviation = np.random.uniform(-0.001, 0.001)
            trade_price = current_price * (1 + deviation)
            trade = {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": trade_price,
                "timestamp": int(time.time())
            }
            # Append the trade event to a Redis list for this symbol
            redis_client.rpush(f"trades:{symbol}", json.dumps(trade))
            # Update order imbalance: increment for buy, decrement for sell
            imbalance_key = f"order_imbalance:{symbol}"
            if side == "buy":
                redis_client.incrby(imbalance_key, quantity)
            else:
                redis_client.decrby(imbalance_key, quantity)
        time.sleep(sleep_time)

def run_orderbook_simulation(symbol, update_interval=10):
    """
    Simulates an orderbook for a given stock symbol.
    Instead of storing bids and asks in one key, this function stores buy orders and sell orders separately.
    """
    print(f"Starting orderbook simulation for {symbol}")
    while True:
        data = redis_client.get(symbol)
        if data:
            try:
                stock = json.loads(data)
                current_price = stock.get("price", 100)
            except Exception:
                current_price = 100
            buy_orders = []
            sell_orders = []
            levels = 5  # Number of price levels for each side
            for i in range(levels):
                offset = np.random.uniform(0.001, 0.005) * (i + 1)
                bid_price = current_price * (1 - offset)
                bid_volume = int(np.random.randint(10, 50))
                buy_orders.append({"price": round(bid_price, 2), "volume": bid_volume})
                ask_price = current_price * (1 + offset)
                ask_volume = int(np.random.randint(10, 50))
                sell_orders.append({"price": round(ask_price, 2), "volume": ask_volume})
            orderbook_buy = {"orders": buy_orders, "timestamp": int(time.time())}
            orderbook_sell = {"orders": sell_orders, "timestamp": int(time.time())}
            redis_client.set(f"orderbook:buy:{symbol}", json.dumps(orderbook_buy))
            redis_client.set(f"orderbook:sell:{symbol}", json.dumps(orderbook_sell))
            print(f"Updated orderbook for {symbol}: buy keys and sell keys stored.")
        else:
            print(f"No stock data for {symbol} found.")
        time.sleep(update_interval)


def simulate_stock_data():
    """
    Starts simulation threads for market data for all defined stocks.
    """
    symbols = {
        "HACK": {"S0": 100, "mu": 0.05, "sigma0": 0.2, "base_volume": 1000, "base_liquidity": 100},
    }
    for symbol, params in symbols.items():
        thread = threading.Thread(target=run_simulation, args=(symbol, params), daemon=True)
        thread.start()

def simulate_trades():
    """
    Starts trade simulation threads for all defined stocks.
    """
    symbols = ["HACK"]
    for symbol in symbols:
        redis_client.set(f"order_imbalance:{symbol}", 0)
        thread = threading.Thread(target=run_trade_simulation, args=(symbol,), daemon=True)
        thread.start()

def simulate_orderbook():
    """
    Starts orderbook simulation threads for all defined stocks.
    """
    symbols = ["HACK"]
    for symbol in symbols:
        thread = threading.Thread(target=run_orderbook_simulation, args=(symbol,), daemon=True)
        thread.start()

if __name__ == "__main__":
    simulate_stock_data()
    simulate_trades()
    simulate_orderbook()
    # Keep the main thread alive.
    while True:
        time.sleep(1)
