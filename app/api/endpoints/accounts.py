# File: stock_market_game/app/api/endpoints/accounts.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import time

from app.database import SessionLocal
from app.models import Account, Position
from app.schemas import AccountData, AccountCreate
from app.redis_client import redis_client
from app.dependencies import verify_admin  # This dependency verifies the admin API key

router = APIRouter()

def compute_networth(cash: float, positions: dict) -> float:
    """
    Computes networth as cash plus the market value of open positions.
    For each symbol in positions, retrieves the current price from Redis.
    """
    networth = cash
    for symbol, quantity in positions.items():
        data = redis_client.get(symbol.upper())
        if data:
            try:
                stock_data = json.loads(data)
                current_price = stock_data.get("price", 0)
                networth += current_price * quantity
            except Exception:
                continue
    return networth

@router.post("/create", response_model=AccountData, dependencies=[Depends(verify_admin)])
def create_account(account: AccountCreate):
    """
    Admin-only endpoint to create a new account.
    If the account already exists, returns the existing account data.
    Computes networth as cash plus the market value of open positions.
    """
    session: Session = SessionLocal()
    try:
        existing = session.query(Account).filter(Account.user_id == account.user_id).first()
        if existing:
            # Build positions dict from positions table if available
            positions_records = session.query(Position).filter(Position.user_id == account.user_id).all()
            positions_dict = { pos.symbol: pos.quantity for pos in positions_records }
            net = compute_networth(existing.cash, positions_dict)
            return AccountData(
                user_id=existing.user_id,
                password=existing.password,  # In production, do not return plain-text passwords.
                cash=existing.cash,
                open_positions=positions_dict,
                profit_loss=existing.profit_loss,
                networth=net
            )
        
        new_account = Account(
            user_id=account.user_id,
            password=account.password,  # In production, hash this password.
            cash=10000.0,
            open_positions={},         # Not used directly now; positions are stored in a separate table.
            profit_loss=0.0
        )
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
        
        # No positions yet, so networth is just cash.
        net = new_account.cash
        
        return AccountData(
            user_id=new_account.user_id,
            password=new_account.password,
            cash=new_account.cash,
            open_positions={},
            profit_loss=new_account.profit_loss,
            networth=net
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.get("/{user_id}", response_model=AccountData)
def get_account(user_id: int):
    """
    Retrieves account information for the given user and computes networth.
    It queries the positions table to build a positions dictionary and then
    computes networth as cash plus the current market value of those positions.
    """
    session: Session = SessionLocal()
    try:
        account = session.query(Account).filter(Account.user_id == user_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        positions_records = session.query(Position).filter(Position.user_id == user_id).all()
        positions_dict = { pos.symbol: pos.quantity for pos in positions_records }
        
        net = compute_networth(account.cash, positions_dict)
        return AccountData(
            user_id=account.user_id,
            password=account.password,  # In production, do not return plain-text passwords.
            cash=account.cash,
            open_positions=positions_dict,
            profit_loss=account.profit_loss,
            networth=net
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
