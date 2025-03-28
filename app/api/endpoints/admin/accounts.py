from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Account
from app.schemas import AccountResponse, AccountStatsResponse, LeaderboardResponse
from app.dependencies import verify_admin
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats", response_model=AccountStatsResponse, dependencies=[Depends(verify_admin)])
def get_account_stats(db: Session = Depends(get_db)):
    """Get account statistics for the admin dashboard."""
    try:
        # Get total users
        total_users = db.query(Account).filter(Account.is_admin == False).count()
        
        # Get yesterday's date
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Get users created today and yesterday
        today_users = db.query(Account).filter(
            Account.is_admin == False,
            Account.created_at >= yesterday
        ).count()
        
        # Calculate percentage change
        change = ((today_users / total_users) * 100) if total_users > 0 else 0
        
        return {
            "total": total_users,
            "change": round(change, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard", response_model=List[LeaderboardResponse], dependencies=[Depends(verify_admin)])
def get_leaderboard(
    limit: int = Query(10, description="Number of users to return"),
    db: Session = Depends(get_db)
):
    """Get the leaderboard of users sorted by net worth."""
    try:
        # Get all non-admin users
        users = db.query(Account).filter(Account.is_admin == False).all()
        
        # Calculate net worth for each user
        user_networths = []
        for user in users:
            # Calculate total value of positions
            positions_value = sum(
                position.quantity * position.current_price 
                for position in user.positions
            )
            
            # Calculate total P/L
            total_pnl = sum(
                (position.current_price - position.average_price) * position.quantity
                for position in user.positions
            )
            
            # Calculate net worth
            net_worth = user.cash + positions_value
            
            user_networths.append({
                "user_id": user.user_id,
                "cash": user.cash,
                "pnl": total_pnl,
                "net_worth": net_worth
            })
        
        # Sort by net worth and take top N
        sorted_users = sorted(
            user_networths,
            key=lambda x: x["net_worth"],
            reverse=True
        )[:limit]
        
        return sorted_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all", response_model=List[AccountResponse], dependencies=[Depends(verify_admin)])
def get_all_accounts(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by user ID or username"),
    db: Session = Depends(get_db)
):
    """Get all accounts with optional filtering."""
    try:
        query = db.query(Account)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Account.user_id.ilike(search_term)) |
                (Account.username.ilike(search_term))
            )
        
        accounts = query.offset(skip).limit(limit).all()
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", response_model=AccountResponse, dependencies=[Depends(verify_admin)])
def create_account_admin(
    username: str,
    password: str,
    initial_cash: float = 10000.0,
    db: Session = Depends(get_db)
):
    """Create a new account (admin endpoint)."""
    try:
        # Check if username already exists
        if db.query(Account).filter(Account.username == username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create new account
        new_account = Account(
            username=username,
            password=password,  # In production, hash the password
            cash=initial_cash,
            is_admin=False
        )
        
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        return new_account
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/create", response_model=AccountResponse, dependencies=[Depends(verify_admin)])
def create_admin_account(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Create a new admin account."""
    try:
        # Check if username already exists
        if db.query(Account).filter(Account.username == username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create new admin account
        new_admin = Account(
            username=username,
            password=password,  # In production, hash the password
            cash=0.0,  # Admins don't need cash
            is_admin=True
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        return new_admin
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify", dependencies=[Depends(verify_admin)])
def verify_admin_credentials(
    admin_id: int,
    db: Session = Depends(get_db)
):
    """Verify admin credentials."""
    try:
        # Check if admin exists and is an admin
        admin = db.query(Account).filter(
            Account.user_id == admin_id,
            Account.is_admin == True
        ).first()
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
        return {"message": "Admin credentials verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 