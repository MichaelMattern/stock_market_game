# File: stock_market_game/app/config.py
import os

# When running inside Docker, the db service is available at hostname "db".
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/stock_market_db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
