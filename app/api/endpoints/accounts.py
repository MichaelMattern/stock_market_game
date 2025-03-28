# File: stock_market_game/app/api/endpoints/accounts.py
from fastapi import APIRouter, HTTPException, Depends, status, Body, Request
from sqlalchemy.orm import Session
import json
import logging
import base64
from app.database import SessionLocal
from app.models import Account, Position
from app.schemas import AccountData, AccountCreate
from app.redis_client import redis_client
from app.dependencies import verify_admin, compute_networth  # Removed verify_user dependency
from typing import Dict, Optional

router = APIRouter()
logger = logging.getLogger(__name__)

# Custom user verification function that's more lenient for the hackathon
def verify_user_hackathon(request: Request, db: Session = Depends(lambda: SessionLocal())):
    """
    User authentication for hackathon purposes.
    Accepts:
    1. Basic Auth with username and password
    2. X-User-ID header
    3. user_id parameter in query or body
    """
    try:
        # Try to get user from authorization header (Basic Auth)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Basic "):
            try:
                credentials = base64.b64decode(auth_header[6:]).decode("utf-8")
                username, password = credentials.split(":", 1)
                user_id = int(username)
                
                user = db.query(Account).filter(Account.user_id == user_id).first()
                if user:
                    # For demo/hackathon, accept either real password or pattern password
                    if user.password == password or password == f"password{user_id}":
                        logger.info(f"User authenticated via Basic Auth: {user_id} (Admin: {user.is_admin})")
                        return user
                    else:
                        logger.warning(f"Invalid password for user: {user_id}")
                        # Log more details about the passwords to help debugging
                        logger.debug(f"Expected: {user.password} or password{user_id}, Got: {password}")
            except Exception as e:
                logger.warning(f"Basic auth failed: {str(e)}")
        
        # Try to get user from X-User-ID header
        user_id_header = request.headers.get("X-User-ID")
        if user_id_header:
            try:
                user_id = int(user_id_header)
                user = db.query(Account).filter(Account.user_id == user_id).first()
                if user:
                    logger.info(f"User authenticated via X-User-ID header: {user_id} (Admin: {user.is_admin})")
                    return user
            except Exception as e:
                logger.warning(f"X-User-ID header auth failed: {str(e)}")
        
        # Try user_id from query parameters
        user_id_param = request.query_params.get("user_id")
        if user_id_param:
            try:
                user_id = int(user_id_param)
                user = db.query(Account).filter(Account.user_id == user_id).first()
                if user:
                    logger.info(f"User authenticated via query param: {user_id} (Admin: {user.is_admin})")
                    return user
            except Exception as e:
                logger.warning(f"Query param auth failed: {str(e)}")
                
        # For admin users (and only in the admin path), check X-Admin-API-Key
        if "admin" in request.url.path:
            admin_key = request.headers.get("x-admin-api-key")
            if admin_key:
                # Get admin_id from request or body
                admin_id = None
                try:
                    # Try to get from path parameter
                    admin_id_str = request.path_params.get("user_id")
                    if admin_id_str:
                        admin_id = int(admin_id_str)
                except Exception:
                    pass
                
                # If we have an admin ID from the URL path, check if they're an admin
                if admin_id:
                    user = db.query(Account).filter(Account.user_id == admin_id, Account.is_admin == True).first()
                    if user and admin_key == "my-secret-admin-key":
                        logger.info(f"Admin authenticated via API key: {admin_id}")
                        return user
        
        # If we couldn't authenticate by now, return 401
        path = request.url.path
        logger.warning(f"Authentication failed for request to: {path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during authentication: {str(e)}"
        )
    finally:
        db.close()

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

@router.post("/authenticate", response_model=Dict[str, str])
def authenticate_user(payload: Dict[str, str] = Body(...)):
    """
    Authenticate a user based on user_id and password.
    Returns a success message if authentication is successful.
    """
    logger.info(f"Authentication attempt received for user: {payload.get('user_id', 'unknown')}")
    logger.info(f"Authentication payload: {payload}")
    
    if "user_id" not in payload or "password" not in payload:
        logger.warning("Authentication missing required fields")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both user_id and password are required"
        )
    
    try:
        user_id = int(payload["user_id"])
        logger.info(f"Parsed user_id: {user_id}")
    except ValueError:
        logger.warning(f"Invalid user_id format: {payload.get('user_id')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format"
        )
        
    password = payload["password"]
    if not password:
        logger.warning("Empty password provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be empty"
        )
    
    session: Session = SessionLocal()
    try:
        user = session.query(Account).filter(Account.user_id == user_id).first()
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        logger.info(f"User found: {user_id}, comparing passwords")
        logger.info(f"User is admin: {user.is_admin}")
        logger.debug(f"Stored password (first char): {user.password[0] if user.password else 'None'}")
        logger.debug(f"Provided password length: {len(password)}")
        
        # Check actual password first
        if user.password == password:
            logger.info(f"Password match successful for user: {user_id}")
            return {
                "message": "Authentication successful", 
                "user_id": str(user_id),
                "is_admin": str(user.is_admin).lower()
            }
            
        # For demo/hackathon, also check pattern password
        if password == f"password{user_id}":
            logger.info(f"Pattern password match successful for user: {user_id}")
            return {
                "message": "Authentication successful", 
                "user_id": str(user_id),
                "is_admin": str(user.is_admin).lower()
            }
        
        # If we get here, authentication failed
        logger.warning(f"Password mismatch for user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.post("/create", include_in_schema=False, response_model=AccountData, dependencies=[Depends(verify_admin)])
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
            # Build positions dict from positions table if available.
            positions_records = session.query(Position).filter(Position.user_id == account.user_id).all()
            positions_dict = { pos.symbol: pos.quantity for pos in positions_records }
            net = compute_networth(existing.cash, positions_dict)
            return AccountData(
                user_id=existing.user_id,
                password=existing.password,  # In production, do not return plain-text passwords.
                cash=existing.cash,
                open_positions=positions_dict,
                profit_loss=existing.profit_loss,
                networth=net,
                is_admin=existing.is_admin
            )
        
        new_account = Account(
            user_id=account.user_id,
            password=account.password,  # In production, hash this password.
            cash=account.initial_cash,
            open_positions={},         # Not used directly; positions are stored in a separate table.
            profit_loss=0.0,
            is_admin=False           # Regular user
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
            networth=net,
            is_admin=new_account.is_admin
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.get("/{user_id}", response_model=AccountData)
def get_account(user_id: int, current_user: Account = Depends(verify_user_hackathon)):
    """
    Retrieves account information for the given user and computes networth.
    Authentication: Only allow access if the authenticated user matches the requested user_id.
    """
    if current_user.user_id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account"
        )
    
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
            networth=net,
            is_admin=account.is_admin
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
