from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Account, Trade, PendingOrder
from app.dependencies import verify_admin

router = APIRouter()

@router.get("/accounts/stats")
def get_account_stats(current_user: Account = Depends(verify_admin)):
    """
    Get statistics about all accounts.
    """
    session: Session = SessionLocal()
    try:
        # Get total number of accounts
        total_accounts = session.query(func.count(Account.id)).scalar()
        
        # Get number of admin accounts
        admin_accounts = session.query(func.count(Account.id)).filter(Account.is_admin == True).scalar()
        
        # Get total cash across all accounts
        total_cash = session.query(func.sum(Account.cash)).scalar() or 0
        
        # Get total profit/loss across all accounts
        total_profit_loss = session.query(func.sum(Account.profit_loss)).scalar() or 0
        
        return {
            "total_accounts": total_accounts,
            "admin_accounts": admin_accounts,
            "regular_accounts": total_accounts - admin_accounts,
            "total_cash": total_cash,
            "total_profit_loss": total_profit_loss,
            "total_networth": total_cash + total_profit_loss
        }
    finally:
        session.close()

@router.get("/trades/stats")
def get_trade_stats(current_user: Account = Depends(verify_admin)):
    """
    Get statistics about all trades.
    """
    session: Session = SessionLocal()
    try:
        # Get total number of trades
        total_trades = session.query(func.count(Trade.id)).scalar()
        
        # Get total volume traded
        total_volume = session.query(func.sum(Trade.quantity)).scalar() or 0
        
        # Get total value traded
        total_value = session.query(func.sum(Trade.quantity * Trade.price)).scalar() or 0
        
        # Get number of unique traders
        unique_traders = session.query(func.count(func.distinct(Trade.user_id))).scalar()
        
        return {
            "total_trades": total_trades,
            "total_volume": total_volume,
            "total_value": total_value,
            "unique_traders": unique_traders,
            "average_trade_value": total_value / total_trades if total_trades > 0 else 0
        }
    finally:
        session.close()

@router.get("/orders/stats")
def get_order_stats(current_user: Account = Depends(verify_admin)):
    """
    Get statistics about all orders.
    """
    session: Session = SessionLocal()
    try:
        # Get total number of pending orders
        total_pending = session.query(func.count(PendingOrder.id)).scalar()
        
        # Get number of buy orders
        buy_orders = session.query(func.count(PendingOrder.id)).filter(PendingOrder.side == "buy").scalar()
        
        # Get number of sell orders
        sell_orders = session.query(func.count(PendingOrder.id)).filter(PendingOrder.side == "sell").scalar()
        
        # Get total volume in pending orders
        total_volume = session.query(func.sum(PendingOrder.quantity)).scalar() or 0
        
        # Get number of unique traders with pending orders
        unique_traders = session.query(func.count(func.distinct(PendingOrder.user_id))).scalar()
        
        return {
            "total_pending_orders": total_pending,
            "buy_orders": buy_orders,
            "sell_orders": sell_orders,
            "total_volume": total_volume,
            "unique_traders": unique_traders
        }
    finally:
        session.close() 