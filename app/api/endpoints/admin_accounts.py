# File: stock_market_game/app/api/endpoints/admin_accounts.py
from fastapi import APIRouter, HTTPException, Depends, Header, Body, Response, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Account, Position, Trade, PendingOrder
from app.schemas import AccountData, AccountCreate, AdminAccountCreate, AdminVerify
from app.dependencies import verify_admin, get_db, compute_networth
import json
from typing import List, Optional

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
        
        # Create a new account with specified initial cash
        new_account = Account(
            user_id=account.user_id,
            password=account.password,  # Remember: in production, hash this password!
            cash=account.initial_cash,
            open_positions={},          # Start with no open positions
            profit_loss=0.0,
            is_admin=False             # Regular user account
        )
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
        
        # Return account with networth
        return AccountData(
            user_id=new_account.user_id,
            password=new_account.password,
            cash=new_account.cash,
            open_positions={},
            profit_loss=new_account.profit_loss,
            networth=new_account.cash,  # Initially networth equals cash
            is_admin=new_account.is_admin
        )
    finally:
        session.close()

@router.post("/admin/create", response_model=AccountData, dependencies=[Depends(verify_admin)])
def create_admin_account(account: AdminAccountCreate):
    """
    Create a new admin account.
    This endpoint is protected by an admin API key.
    """
    session: Session = SessionLocal()
    try:
        existing = session.query(Account).filter(Account.user_id == account.user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Account already exists")
        
        # Create a new admin account
        new_account = Account(
            user_id=account.user_id,
            password=account.password,  # Remember: in production, hash this password!
            cash=account.initial_cash,
            open_positions={},          # Start with no open positions
            profit_loss=0.0,
            is_admin=True              # Admin account
        )
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
        
        # Return account with networth
        return AccountData(
            user_id=new_account.user_id,
            password=new_account.password,
            cash=new_account.cash,
            open_positions={},
            profit_loss=new_account.profit_loss,
            networth=new_account.cash,  # Initially networth equals cash
            is_admin=new_account.is_admin
        )
    finally:
        session.close()

@router.get("/", response_model=List[AccountData], dependencies=[Depends(verify_admin)])
def get_all_accounts(db: Session = Depends(get_db)):
    """
    Get all accounts.
    This endpoint is protected by an admin API key.
    """
    accounts = db.query(Account).all()
    
    # Calculate networth for each account
    result = []
    for account in accounts:
        # Build positions dict from positions table
        positions_records = db.query(Position).filter(Position.user_id == account.user_id).all()
        positions_dict = {pos.symbol: pos.quantity for pos in positions_records}
        
        # Calculate networth
        networth = compute_networth(account.cash, positions_dict)
        
        result.append(AccountData(
            user_id=account.user_id,
            password=account.password,  # In production, do not return plain-text passwords
            cash=account.cash,
            open_positions=positions_dict,
            profit_loss=account.profit_loss,
            networth=networth,
            is_admin=account.is_admin
        ))
    
    return result

@router.get("/{user_id}", response_model=AccountData, dependencies=[Depends(verify_admin)])
def get_account_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Get account by user ID.
    This endpoint is protected by an admin API key.
    """
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Build positions dict from positions table
    positions_records = db.query(Position).filter(Position.user_id == user_id).all()
    positions_dict = {pos.symbol: pos.quantity for pos in positions_records}
    
    # Calculate networth
    networth = compute_networth(account.cash, positions_dict)
    
    return AccountData(
        user_id=account.user_id,
        password=account.password,  # In production, do not return plain-text passwords
        cash=account.cash,
        open_positions=positions_dict,
        profit_loss=account.profit_loss,
        networth=networth,
        is_admin=account.is_admin
    )

@router.delete("/{user_id}", dependencies=[Depends(verify_admin)])
def delete_account(user_id: int, db: Session = Depends(get_db)):
    """
    Delete account by user ID.
    This endpoint is protected by an admin API key.
    """
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Delete related data first
    db.query(Position).filter(Position.user_id == user_id).delete()
    db.query(Trade).filter(Trade.user_id == user_id).delete()
    db.query(PendingOrder).filter(PendingOrder.user_id == user_id).delete()
    
    # Delete the account
    db.delete(account)
    db.commit()
    
    return {"message": f"Account {user_id} deleted successfully"}

@router.post("/{user_id}/reset-password", dependencies=[Depends(verify_admin)])
def reset_password(user_id: int, password_data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Reset account password.
    This endpoint is protected by an admin API key.
    """
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update password
    account.password = password_data.get("password")
    db.commit()
    
    return {"message": f"Password for account {user_id} reset successfully"}

@router.post("/{user_id}/reset-cash", dependencies=[Depends(verify_admin)])
def reset_cash(user_id: int, cash_data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Reset account cash balance.
    This endpoint is protected by an admin API key.
    """
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update cash balance
    account.cash = cash_data.get("cash", 10000.0)
    db.commit()
    
    return {"message": f"Cash balance for account {user_id} reset successfully"}

@router.post("/verify", dependencies=[Depends(verify_admin)])
def verify_admin_credentials(admin_data: AdminVerify):
    """
    Verify admin credentials.
    This endpoint is used by the admin panel to verify login.
    """
    # The verify_admin dependency already checked the API key,
    # so if we get here, the API key is valid.
    # Just check if the admin_id exists
    session: Session = SessionLocal()
    try:
        admin = session.query(Account).filter(
            Account.user_id == admin_data.admin_id, 
            Account.is_admin == True
        ).first()
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
        return {"message": "Admin verified successfully"}
    finally:
        session.close()
