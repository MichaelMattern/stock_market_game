from app.database import SessionLocal
from sqlalchemy import inspect
import time
from datetime import datetime

# Connect to the database
session = SessionLocal()
inspector = inspect(session.bind)

# Print the tables in the database
print("Tables in the database:")
for table_name in inspector.get_table_names():
    print(f"  - {table_name}")

# Print the columns in the historical_stock_data table
print("\nColumns in historical_stock_data:")
for column in inspector.get_columns("historical_stock_data"):
    print(f"  - {column['name']}: {column['type']}")

# Create a new historical_stock_data entry
try:
    from app.models import StockHistory

    # Create test data
    history = StockHistory(
        symbol="HACK",
        price=100.0,
        volume=1000.0,
        volatility=0.2,
        timestamp=datetime.now(),
        liquidity=100.0,
        interval="1m"
    )
    
    print("\nAttempting to insert data...")
    session.add(history)
    session.commit()
    print("Successfully inserted test data")
    
    # Verify the data was inserted
    count = session.query(StockHistory).count()
    print(f"Historical data count: {count}")
    
except Exception as e:
    print(f"Error: {e}")
    session.rollback()

session.close() 