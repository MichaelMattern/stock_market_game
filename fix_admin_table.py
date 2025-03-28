"""
Direct SQL script to add is_admin column to accounts table.
This bypasses Alembic to fix the migration issues.
"""
from sqlalchemy import create_engine, text
import os
import time

# Get database connection URL from environment or use default
db_url = os.environ.get("DATABASE_URL", "postgresql://user:password@db/stock_market_db")
print(f"Using database URL: {db_url}")

# Create SQLAlchemy engine
engine = create_engine(db_url)

# Function to check if a column exists
def column_exists(connection, table, column):
    result = connection.execute(text(
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_name='{table}' AND column_name='{column}'"
    ))
    return bool(result.fetchone())

# Function to check if a user exists
def user_exists(connection, user_id):
    result = connection.execute(text(
        f"SELECT user_id FROM accounts WHERE user_id = {user_id}"
    ))
    return bool(result.fetchone())

try:
    with engine.connect() as connection:
        # Start transaction
        transaction = connection.begin()
        
        try:
            # Step 1: Check if is_admin column exists
            has_column = column_exists(connection, 'accounts', 'is_admin')
            
            if has_column:
                print("is_admin column already exists")
            else:
                print("is_admin column does not exist, will add it")
                
                # Step 2: Add is_admin column if it doesn't exist
                connection.execute(text(
                    "ALTER TABLE accounts ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"
                ))
                print("Added is_admin column")
            
            # Wait a moment for the schema change to be fully applied
            time.sleep(1)
            
            # Step 3: Get info about user 1000
            admin_exists = user_exists(connection, 1000)
            
            if admin_exists:
                print("User ID 1000 already exists, updating admin status")
                # Update existing user to be admin
                connection.execute(text(
                    "UPDATE accounts SET is_admin = TRUE WHERE user_id = 1000"
                ))
                print("Updated user 1000 to admin")
            else:
                print("Creating admin user with ID 1000")
                # Create new admin user
                connection.execute(text(
                    "INSERT INTO accounts (user_id, password, cash, open_positions, profit_loss, is_admin) "
                    "VALUES (1000, 'admin', 10000.0, '{}', 0.0, TRUE)"
                ))
                print("Created admin user")
            
            # Commit the transaction
            transaction.commit()
            print("Database updated successfully")
            
            # Verify admin user
            print("Verifying admin user...")
            admin_check = connection.execute(text(
                "SELECT user_id, password FROM accounts WHERE user_id = 1000"
            ))
            admin = admin_check.fetchone()
            if admin:
                print(f"Admin user exists: ID={admin[0]}, Password={admin[1]}")
                # Update to admin if not already
                connection.execute(text(
                    "UPDATE accounts SET is_admin = TRUE WHERE user_id = 1000"
                ))
                print("Ensured user has admin privileges")
            else:
                print("No admin user found with ID 1000")
                
        except Exception as e:
            # Rollback on error
            transaction.rollback()
            raise e
            
except Exception as e:
    print(f"Database error: {e}")
    print("Please restart the container to apply the changes") 