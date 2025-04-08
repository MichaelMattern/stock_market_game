import logging
from sqlalchemy import text, MetaData
from app.database import SessionLocal, engine, Base
from app.models import Account  # Import Account to ensure models are registered

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_database():
    """
    Truncates all user-defined tables and reseeds the admin user.
    """
    logger.info("Starting database reset process...")
    session = SessionLocal()
    try:
        # Get metadata from Base
        metadata = Base.metadata
        table_names = [table.name for table in metadata.tables.values()]

        # Exclude alembic version table if necessary (though TRUNCATE usually skips system tables)
        if 'alembic_version' in table_names:
            table_names.remove('alembic_version')

        if not table_names:
            logger.warning("No user-defined tables found in metadata. Exiting.")
            return

        logger.info(f"Identified tables to truncate: {', '.join(table_names)}")

        # Construct the TRUNCATE command
        # Using RESTART IDENTITY to reset primary key sequences
        # Using CASCADE to handle foreign key constraints
        truncate_command = f"TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE;"
        logger.info(f"Executing: {truncate_command}")
        session.execute(text(truncate_command))
        logger.info("Tables truncated successfully.")

        # Re-seed the admin user
        # Based on alembic/versions/add_is_admin_field.py
        reseed_admin_command = """
        INSERT INTO accounts (user_id, password, cash, open_positions, profit_loss, is_admin)
        SELECT 1000, 'admin', 10000.0, '{}', 0.0, True
        WHERE NOT EXISTS (SELECT 1 FROM accounts WHERE user_id = 1000);
        """
        logger.info("Reseeding admin user (user_id=1000)...")
        session.execute(text(reseed_admin_command))
        logger.info("Admin user reseeded successfully.")

        session.commit()
        logger.info("Database reset complete and changes committed.")

    except Exception as e:
        logger.error(f"An error occurred during database reset: {e}")
        session.rollback()
        logger.info("Transaction rolled back due to error.")
    finally:
        session.close()
        logger.info("Database session closed.")

if __name__ == "__main__":
    confirmation = input("Are you sure you want to truncate all data and reset the database? (yes/no): ")
    if confirmation.lower() == 'yes':
        reset_database()
    else:
        print("Database reset cancelled.") 