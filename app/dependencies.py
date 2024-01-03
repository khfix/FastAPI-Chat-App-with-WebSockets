from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import ALGORITHM, SECRET_KEY
from app.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), secret_key: str = Depends(lambda: ALGORITHM)
):
    """
    Retrieves the current user based on the provided token and secret key.

    Args:
        token (str): The authentication token.
        secret_key (str): The secret key used for decoding the token.

    Returns:
        str: The user ID extracted from the token.

    Raises:
        HTTPException: If the authentication credentials are invalid.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id


def get_db():
    """
    Get a database session.

    Returns:
        SessionLocal: The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
