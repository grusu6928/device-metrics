"""FastAPI dependencies"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.common.database import get_db
from src.common.auth import decode_access_token, get_password_hash
from src.models.user import User
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def create_test_user(db: Session):
    """Create a test user for development"""
    test_user = get_user_by_username(db, "testuser")
    if not test_user:
        logger.info("Creating test user: testuser / testpassword")
        test_user = User(
            username="testuser",
            password_hash=get_password_hash("testpassword")
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> dict:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return {"username": user.username, "id": user.id}

