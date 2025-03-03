# File: stock_market_game/app/api/endpoints/admin_accounts.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Account
from app.schemas import AccountData, AccountCreate
from app.dependencies import verify_admin

router = APIRouter()

@router.post("/create", response_model=AccountData, dependencies=[Depends(verify_admin)])
def create_account_admin(account: AccountCreate):
    """
    Admin endpoint to create a new user account.
    This endpoint is protected by an admin API key.
    """
    session: Session = SessionLocal()
    try:
        existing = session.query(Account).filter(Account.user_id == account.user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Account already exists")
        
        # Create a new account; cash is initialized to a default value (e.g., 10000)
        new_account = Account(
            user_id=account.user_id,
            password=account.password,  # Remember: in production, hash this password!
            cash=10000.0,
            open_positions={},          # Start with no open positions
            profit_loss=0.0
        )
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
        
        # Initially, networth equals cash (since open_positions is empty)
        # The AccountData schema will be populated with networth in a later computed step if desired.
        return new_account
    finally:
        session.close()
