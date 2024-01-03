# app/user.py

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import ALGORITHM, SECRET_KEY
from app.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter()


def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticates a user by checking if the provided username and password match the user's credentials in the database.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        db (Session): The database session.

    Returns:
        User: The authenticated user if the credentials are valid, None otherwise.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create an access token.

    Args:
        data (dict): The data to be encoded in the token.
        expires_delta (timedelta, optional): The expiration time delta for the token. Defaults to None.

    Returns:
        str: The encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    """
    Verify if a plain password matches a hashed password.

    Args:
        plain_password (str): The plain password to be verified.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the plain password matches the hashed password, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    """
    Endpoint to access a protected resource.

    Args:
        current_user (str): The current user accessing the resource.

    Returns:
        dict: A dictionary containing a message confirming access to the protected resource.
    """
    return {
        "message": f"Hello {current_user}, you have access to this protected resource"
    }


@router.post("/create_user/{username}")
async def create_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Create a new user with the given username and password.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the message "User created successfully".
    """
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}


@router.delete("/delete_user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user from the database.

    Args:
        user_id (int): The ID of the user to delete.
        db (Session): The database session.

    Returns:
        dict: A dictionary with a message indicating the success of the operation.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@router.post("/token", response_model=dict)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Logs in a user and returns an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the access token, token type, and user ID.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "id": user.id}
