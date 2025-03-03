# File: stock_market_game/app/api/endpoints/leaderboard.py
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Account
from app.schemas import LeaderboardEntry

router = APIRouter()

@router.get("/", response_model=list[LeaderboardEntry])
def get_leaderboard():
    """
    Retrieves all user accounts, computes networth for each account as:
         networth = cash + profit_loss
    and returns a leaderboard sorted in descending order by networth.
    """
    session: Session = SessionLocal()
    try:
        accounts = session.query(Account).all()
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found")
        
        leaderboard = []
        for account in accounts:
            # Compute networth dynamically
            networth = account.cash + account.profit_loss
            leaderboard.append({
                "user_id": account.user_id,
                "cash": account.cash,
                "profit_loss": account.profit_loss,
                "networth": networth,
            })
        
        # Sort the leaderboard by networth in descending order
        leaderboard.sort(key=lambda x: x["networth"], reverse=True)
        return leaderboard
    finally:
        session.close()
