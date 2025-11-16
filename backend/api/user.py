from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
import logging

from core import database
from core.exceptions import create_error_response, log_error
from schemas.user import TokenData, User, UserCreate
from passlib.context import CryptContext

# Configure logging
logger = logging.getLogger(__name__)

#密钥,用于认证
import os
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key")  # Should be set in environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300000

#登陆相关
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, id=user_id)
    except JWTError:
        raise credentials_exception
    
    # We now have the ID and username directly from the token.
    # We can create the User object without another DB call if we trust the token.
    if token_data.id is None or token_data.username is None:
        raise credentials_exception
    return User(id=token_data.id, username=token_data.username)

router = APIRouter()

@router.post("/login")
def login_for_access_token(form_data: UserCreate):
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        user_dict = database.get_user_by_username(username=form_data.username)
        if not user_dict or not isinstance(user_dict, dict) or 'password' not in user_dict or not verify_password(form_data.password, user_dict['password']):
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            return create_error_response(
                401,
                "Incorrect username or password"
            )
        # Include both username and id in the token
        access_token = create_access_token(data={"sub": user_dict.get('username'), "id": user_dict.get('id')})
        logger.info(f"Successful login for user: {form_data.username}")
        return JSONResponse(
            status_code=200,
            content={"code": 200, "message": "Login successful", "data": {"token": access_token}}
        )
    except Exception as e:
        logger.error(f"Error during login: {e}")
        log_error(e, "login_for_access_token")
        return create_error_response(
            500,
            "Internal server error occurred during login"
        )

@router.post("/register")
def register_user(user_data: UserCreate):
    try:
        logger.info(f"Registration attempt for user: {user_data.username}")
        if database.get_user_by_username(user_data.username):
            logger.warning(f"Registration failed: username {user_data.username} already exists")
            return create_error_response(
                409,
                "Username already registered"
            )

        hashed_password = get_password_hash(user_data.password)
        success = database.create_user(user_data.username, hashed_password)

        if success:
            logger.info(f"Successfully registered user: {user_data.username}")
            return JSONResponse(
                status_code=201,
                content={"code": 201, "message": "User registered successfully"}
            )
        else:
            logger.error(f"Failed to create user: {user_data.username}")
            return create_error_response(
                500,
                "Failed to create user"
            )
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        log_error(e, "register_user")
        return create_error_response(
            500,
            "Internal server error occurred during registration"
        )
