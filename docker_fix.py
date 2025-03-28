"""
Docker Admin Authentication Verification Script

This script helps diagnose and fix issues with admin authentication in Docker environments.
Run this script to:
1. Check if admin user exists in the database
2. Verify database connection settings
3. Create admin user if needed
4. Test admin API endpoint access
"""
import os
import sys
import requests
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Configuration
ADMIN_API_KEY = "my-secret-admin-key"
ADMIN_USER_ID = 1000
ADMIN_PASSWORD = "admin"

def check_environment():
    """Check for Docker environment variables"""
    print("\n=== Environment Check ===")
    
    # Check Docker environment variables
    db_url = os.environ.get("DATABASE_URL")
    redis_host = os.environ.get("REDIS_HOST")
    print(f"DATABASE_URL: {db_url or 'Not set'}")
    print(f"REDIS_HOST: {redis_host or 'Not set'}")
    
    # Get container info
    try:
        hostname = subprocess.check_output("hostname", shell=True).decode().strip()
        print(f"Container hostname: {hostname}")
    except:
        print("Failed to get hostname, might not be in Docker")
    
    # Get network info
    try:
        print("\nNetwork configuration:")
        subprocess.run("ip addr | grep inet", shell=True)
    except:
        print("Failed to get network info")

def test_database_connection():
    """Test database connection and admin account"""
    print("\n=== Database Connection ===")
    
    # Get database URL from environment or use default
    db_url = os.environ.get("DATABASE_URL", "postgresql://user:password@db/stock_market_db")
    print(f"Using database URL: {db_url}")
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test connection
        result = session.execute(text("SELECT 1")).fetchone()
        print(f"Database connection test: {'Successful' if result else 'Failed'}")
        
        # Check if admin table exists
        try:
            result = session.execute(text("SELECT COUNT(*) FROM account WHERE is_admin = TRUE")).fetchone()
            admin_count = result[0] if result else 0
            print(f"Admin users found: {admin_count}")
            
            if admin_count > 0:
                # Get admin details
                admin = session.execute(
                    text("SELECT user_id, password FROM account WHERE is_admin = TRUE LIMIT 1")
                ).fetchone()
                print(f"Admin user: ID={admin[0]}, Password={admin[1]}")
            else:
                print("No admin users found. Consider running setup_admin.py")
                
        except Exception as e:
            print(f"Error checking admin users: {e}")
            
    except Exception as e:
        print(f"Database connection error: {e}")
    finally:
        if 'session' in locals():
            session.close()

def test_api_endpoints():
    """Test API endpoints related to admin authentication"""
    print("\n=== API Endpoint Test ===")
    
    # Base URL - try both localhost and container service name
    base_urls = [
        "http://localhost:8000",
        "http://web:8000",  # Docker service name
        "http://127.0.0.1:8000"
    ]
    
    for base_url in base_urls:
        print(f"\nTesting with base URL: {base_url}")
        
        # Test admin verification endpoint
        admin_verify_url = f"{base_url}/admin/accounts/verify"
        print(f"Testing admin verify endpoint: {admin_verify_url}")
        
        try:
            response = requests.post(
                admin_verify_url,
                headers={"x-admin-api-key": ADMIN_API_KEY, "Content-Type": "application/json"},
                json={"admin_id": ADMIN_USER_ID},
                timeout=5
            )
            
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Admin verification successful!")
            else:
                print("❌ Admin verification failed!")
        except Exception as e:
            print(f"Error testing endpoint: {e}")
    
    print("\nAPI Endpoint Note:")
    print("- If all tests failed, check if FastAPI is running")
    print("- If using Docker, make sure services can communicate")
    print("- From browser, API base URL should match window.location.origin")

def print_browser_instructions():
    """Print instructions for browser debugging"""
    print("\n=== Browser Debugging ===")
    print("Add this code to your browser console when on the admin login page:")
    print("""
console.log('Window location:', {
    href: window.location.href,
    origin: window.location.origin,
    host: window.location.host,
    hostname: window.location.hostname,
    protocol: window.location.protocol,
    port: window.location.port
});

// Test API connection
fetch(window.location.origin + '/admin/accounts/verify', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'x-admin-api-key': 'my-secret-admin-key'
    },
    body: JSON.stringify({ admin_id: 1000 })
})
.then(response => {
    console.log('API Response status:', response.status);
    return response.text();
})
.then(data => console.log('API Response:', data))
.catch(error => console.error('API Error:', error));
    """)

if __name__ == "__main__":
    print("=== Docker Admin Authentication Fix ===")
    
    check_environment()
    test_database_connection()
    test_api_endpoints()
    print_browser_instructions()
    
    print("\n=== Summary ===")
    print("1. Ensure admin user exists in database")
    print("2. Verify admin API endpoint is accessible")
    print("3. Check network connectivity between services")
    print("4. Use browser console to debug login.html")
    print("5. Ensure API_BASE_URL correctly uses window.location.origin")
    print("\nIf issues persist, try running setup_admin.py to recreate admin user") 