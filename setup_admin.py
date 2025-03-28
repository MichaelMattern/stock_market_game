"""
Run this script to add the is_admin field to the accounts table and create an admin user.
"""
import os
import sys
import subprocess

def run_alembic_migration():
    print("Running Alembic migration to add is_admin field...")
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error running Alembic migration:")
        print(result.stderr)
        return False
    else:
        print("Alembic migration successful.")
        print(result.stdout)
        return True

def create_admin_user():
    print("\nCreating admin user through Python...")
    
    try:
        from app.database import SessionLocal
        from app.models import Account
        from sqlalchemy.orm import Session
        
        session: Session = SessionLocal()
        
        # Check if admin user exists
        admin = session.query(Account).filter(Account.is_admin == True).first()
        
        if admin:
            print(f"Admin user already exists (ID: {admin.user_id})")
            print("Admin credentials:")
            print(f"User ID: {admin.user_id}")
            print(f"Password: {admin.password}")
            print(f"API Key: my-secret-admin-key")
            return True
        
        # Create admin user
        admin_user = Account(
            user_id=1000,
            password="admin",  # You should use a more secure password in production
            cash=10000.0,
            open_positions={},
            profit_loss=0.0,
            is_admin=True
        )
        
        session.add(admin_user)
        session.commit()
        
        print("Admin user created successfully!")
        print("Admin credentials:")
        print("User ID: 1000")
        print("Password: admin")
        print("API Key: my-secret-admin-key")
        
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False
    finally:
        session.close() if 'session' in locals() else None

if __name__ == "__main__":
    print("=== Admin Setup Script ===")
    
    # Run Alembic migration
    migration_success = run_alembic_migration()
    
    # Create admin user
    user_success = create_admin_user()
    
    if migration_success and user_success:
        print("\n=== Setup Completed Successfully ===")
        print("You can now log in to the admin panel at:")
        print("http://localhost:8000/static/admin/login.html")
        print("with the admin credentials shown above.")
    else:
        print("\n=== Setup Completed with Errors ===")
        print("Please fix the errors above and try again.")
        sys.exit(1) 