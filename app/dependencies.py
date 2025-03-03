# File: stock_market_game/app/dependencies.py
from fastapi import Header, HTTPException, Depends

def verify_admin(x_admin_api_key: str = Header(...)):
    # Replace "my-secret-admin-key" with your actual secure admin key.
    if x_admin_api_key != "my-secret-admin-key":
        raise HTTPException(status_code=401, detail="Unauthorized: Admin key invalid")
    return True
