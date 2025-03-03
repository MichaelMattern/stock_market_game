# File: stock_market_game/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

print("DATABASE_URL =", DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables if they don't exist (for development purposes)
def init_db():
    import app.models  # Ensure all models are imported so they are registered with Base
    Base.metadata.create_all(bind=engine)

# Optionally, call init_db() in your app startup
if __name__ == "__main__":
    init_db()
