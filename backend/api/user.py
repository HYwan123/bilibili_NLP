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
from schemas.user import TokenData, User, UserCreate, UserProfile, UserProfileUpdate
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
            # 获取新创建的用户信息以生成token
            new_user = database.get_user_by_username(user_data.username)
            if new_user:
                # 生成访问令牌
                access_token = create_access_token(data={"sub": new_user.get('username'), "id": new_user.get('id')})
                logger.info(f"Successfully registered user: {user_data.username}")
                return JSONResponse(
                    status_code=201,
                    content={"code": 201, "message": "User registered successfully", "data": {"token": access_token}}
                )
            else:
                logger.error(f"Failed to retrieve newly created user: {user_data.username}")
                return create_error_response(
                    500,
                    "Failed to retrieve user after registration"
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


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    获取当前用户的个人资料
    """
    try:
        logger.info(f"User {current_user.username} ({current_user.id}) requesting profile")

        # Ensure the user profile table exists
        database.create_user_profile_table()

        profile = database.get_user_profile(current_user.id)

        if not profile:
            # If user profile doesn't exist, create a default one
            default_profile = {
                'user_id': current_user.id,
                'nickname': current_user.username,
                'avatar': None,
                'email': None,
                'phone': None,
                'gender': 'not_set',
                'birth_date': None,
                'bio': None,
                'location': None,
                'occupation': None
            }

            success = database.create_user_profile(current_user.id, default_profile)
            if success:
                profile = database.get_user_profile(current_user.id)

        if profile:
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "Profile retrieved successfully", "data": profile}
            )
        else:
            return create_error_response(
                404,
                "Profile not found"
            )
    except Exception as e:
        logger.error(f"Error retrieving profile for user {current_user.id}: {e}")
        log_error(e, "get_user_profile")
        return create_error_response(
            500,
            "Internal server error occurred while retrieving profile"
        )


@router.post("/profile")
async def create_or_update_user_profile(profile_data: UserProfileUpdate, current_user: User = Depends(get_current_user)):
    """
    创建或更新用户个人资料
    """
    try:
        logger.info(f"User {current_user.username} ({current_user.id}) updating profile")

        # Ensure the user profile table exists
        database.create_user_profile_table()

        # Prepare the profile data dictionary
        profile_dict = profile_data.dict(exclude_unset=True)

        # Check if profile exists
        existing_profile = database.get_user_profile(current_user.id)
        if existing_profile:
            # Update existing profile
            success = database.update_user_profile(current_user.id, profile_dict)
            if success:
                # Get updated profile to return
                updated_profile = database.get_user_profile(current_user.id)
                return JSONResponse(
                    status_code=200,
                    content={"code": 200, "message": "Profile updated successfully", "data": updated_profile}
                )
            else:
                return create_error_response(
                    400,
                    "Failed to update profile"
                )
        else:
            # Create new profile
            profile_dict['user_id'] = current_user.id
            success = database.create_user_profile(current_user.id, profile_dict)
            if success:
                # Get created profile to return
                created_profile = database.get_user_profile(current_user.id)
                return JSONResponse(
                    status_code=201,
                    content={"code": 201, "message": "Profile created successfully", "data": created_profile}
                )
            else:
                return create_error_response(
                    400,
                    "Failed to create profile"
                )
    except Exception as e:
        logger.error(f"Error updating profile for user {current_user.id}: {e}")
        log_error(e, "create_or_update_user_profile")
        return create_error_response(
            500,
            "Internal server error occurred while updating profile"
        )


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_user_profile_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    """
    获取指定用户的个人资料
    """
    try:
        logger.info(f"User {current_user.username} ({current_user.id}) requesting profile for user_id {user_id}")

        # Only allow users to access their own profile for now (can be extended with permissions)
        if current_user.id != user_id:
            return create_error_response(
                403,
                "Access denied. You can only access your own profile."
            )

        profile = database.get_user_profile(user_id)
        if profile:
            return JSONResponse(
                status_code=200,
                content={"code": 200, "message": "Profile retrieved successfully", "data": profile}
            )
        else:
            return create_error_response(
                404,
                "Profile not found"
            )
    except Exception as e:
        logger.error(f"Error retrieving profile for user_id {user_id}: {e}")
        log_error(e, "get_user_profile_by_id")
        return create_error_response(
            500,
            "Internal server error occurred while retrieving profile"
        )
