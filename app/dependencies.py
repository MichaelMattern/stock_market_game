# dependencies.py contains the dependencies for verifying the user and admin
from fastapi import Header, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from sqlalchemy.orm import Session
from app.database import SessionLocal

# Admin verification dependency.
def verify_admin(x_admin_api_key: str = Header(...)):
    # Replace "my-secret-admin-key" with your actual secure admin key.
    if x_admin_api_key != "my-secret-admin-key":
        raise HTTPException(status_code=401, detail="Unauthorized: Admin key invalid")
    return True

# Database session dependency.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize HTTP Basic security.
security = HTTPBasic()

# User verification dependency using HTTP Basic.
def verify_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        # Expecting the username to be the user_id.
        user_id = int(credentials.username)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user_id format"
        )

    from app.models import Account  # Import here to avoid circular dependencies.
    user = db.query(Account).filter(Account.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Compare the provided password securely with the stored password.
    if not secrets.compare_digest(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    return user
