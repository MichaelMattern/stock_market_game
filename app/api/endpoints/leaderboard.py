# File: stock_market_game/app/api/endpoints/leaderboard.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Account, Position  # Import Position model
from app.schemas import LeaderboardEntry, AdminLeaderboardEntry
from app.redis_client import redis_client
from app.dependencies import verify_admin, get_db
import json

router = APIRouter()

def get_current_price(symbol: str) -> float:
    """Helper function to get the current price of a stock from Redis."""
    stock_data = redis_client.get(symbol.upper())
    if stock_data:
        try:
            data = json.loads(stock_data)
            return data.get("price", 0.0)
        except json.JSONDecodeError:
            return 0.0
    return 0.0

@router.get("/", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Retrieves all user accounts, calculates the market value of their open
    positions based on current stock prices from the Position table,
    computes networth as:
         networth = cash + market_value
    and returns a leaderboard (user_id, networth) sorted in descending order by networth.
    """
    try:
        accounts = db.query(Account).all()
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found")

        leaderboard = []
        for account in accounts:
            # Query the Position table for this user's holdings
            user_positions = db.query(Position).filter(Position.user_id == account.user_id).all()

            market_value = 0.0
            if user_positions:
                for position in user_positions:
                    if position.quantity > 0: # Only consider held positions
                        current_price = get_current_price(position.symbol)
                        market_value += (position.quantity * current_price)

            # Compute networth using cash and market value
            networth = round((account.cash or 0) + market_value, 2)

            leaderboard.append({
                "user_id": account.user_id,
                "networth": networth,
            })

        # Sort the leaderboard by networth in descending order
        leaderboard.sort(key=lambda x: x["networth"], reverse=True)
        return leaderboard
    finally:
        pass

@router.get("/admin", response_model=list[AdminLeaderboardEntry], dependencies=[Depends(verify_admin)])
def get_admin_leaderboard(db: Session = Depends(get_db)):
    """
    Admin endpoint: Retrieves all user accounts with detailed financial info.
    Profit/Loss is calculated as total Net Worth - Starting Cash (10000).
    Requires admin authentication.
    """
    try:
        accounts = db.query(Account).all()
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found")

        leaderboard = []
        starting_cash = 10000.0 # Define starting cash amount

        for account in accounts:
            # Query the Position table for this user's holdings
            user_positions = db.query(Position).filter(Position.user_id == account.user_id).all()

            market_value = 0.0
            if user_positions:
                for position in user_positions:
                    if position.quantity > 0: # Only consider held positions
                        current_price = get_current_price(position.symbol)
                        market_value += (position.quantity * current_price)

            # Compute networth using cash and market value
            networth = round((account.cash or 0) + market_value, 2)

            # Calculate total profit/loss relative to starting cash
            total_profit_loss = round(networth - starting_cash, 2)

            # Append detailed info for admin
            leaderboard.append({
                "user_id": account.user_id,
                "cash": round(account.cash or 0, 2),
                "profit_loss": total_profit_loss, # Use calculated total P/L
                "market_value": round(market_value, 2),
                "networth": networth,
            })

        # Sort the leaderboard by networth in descending order
        leaderboard.sort(key=lambda x: x["networth"], reverse=True)
        return leaderboard
    finally:
        # Session closing is handled automatically when using Depends
        pass # No need for db.close() here
