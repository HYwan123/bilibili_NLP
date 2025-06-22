from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
import json

from . import bilibili, database, vector_db, kafka_producer, sql_use

# --- Configuration ---
SECRET_KEY = "your_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- FastAPI App Initialization ---
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None

# --- Security and Authentication ---
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
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, id=user_id)
    except JWTError:
        raise credentials_exception
    
    # We now have the ID and username directly from the token.
    # We can create the User object without another DB call if we trust the token.
    return User(id=token_data.id, username=token_data.username)


# --- API Routers ---
user_router = APIRouter(prefix="/user", tags=["user"])
api_router = APIRouter(prefix="/api", tags=["api"])

# --- User Authentication Routes ---
@user_router.post("/login")
def login_for_access_token(form_data: UserCreate):
    user_dict = database.get_user_by_username(username=form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict['password']):
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "Incorrect username or password"}
        )
    # Include both username and id in the token
    access_token = create_access_token(data={"sub": user_dict['username'], "id": user_dict['id']})
    return JSONResponse(
        status_code=200,
        content={"code": 200, "message": "Login successful", "data": {"token": access_token}}
    )

@user_router.post("/register")
def register_user(user_data: UserCreate):
    if database.get_user_by_username(user_data.username):
        return JSONResponse(
            status_code=409,
            content={"code": 409, "message": "Username already registered"}
        )
    
    hashed_password = get_password_hash(user_data.password)
    success = database.create_user(user_data.username, hashed_password)

    if success:
        return JSONResponse(status_code=201, content={"code": 201, "message": "User registered successfully"})
    else:
        return JSONResponse(status_code=500, content={"code": 500, "message": "Failed to create user"})

# --- Core Bilibili Data Routes ---
@api_router.get("/select/{BV}")
async def select_BV(BV: str, current_user: User = Depends(get_current_user)):
    result = bilibili.select_by_BV(BV)
    
    # Prepare data for history record
    if result:
        # Extract comment texts and create a summary
        comment_texts = [comment.get('comment_text', '') for comment in result if comment.get('comment_text')]
        if comment_texts:
            # Create a summary of the first few comments (limit to avoid too long data)
            summary = f"爬取到 {len(comment_texts)} 条评论，前3条: " + " | ".join(comment_texts[:3])
            if len(comment_texts) > 3:
                summary += f" ... (还有 {len(comment_texts) - 3} 条)"
        else:
            summary = "未获取到评论内容"
    else:
        summary = "查询失败，未获取到数据"
    
    # Add to history with the summary data
    database.add_bv_history(BV, current_user.username, summary)
    
    if result:
        return JSONResponse(status_code=200, content={'code': 200, 'message': 'success', 'data': result})
    else:
        return JSONResponse(status_code=404, content={'code': 404, 'message': 'Not Found', 'data': None})

@api_router.post("/user/analysis/{uid}")
async def get_user_analysis(uid: int, current_user: User = Depends(get_current_user)):
    job_id = str(uuid.uuid4())
    job_data = {"uid": uid, "job_id": job_id}
    
    # --- Record history with job_id ---
    try:
        database.add_uuid_history(uid=str(uid), username=current_user.username, job_id=job_id)
    except Exception as e:
        # Log the error but don't block the job submission
        print(f"Error adding UUID history to database: {e}")

    redis_handler = sql_use.SQL_redis()
    
    # Set initial status in Redis
    initial_status = {"status": "Queued", "progress": 5, "details": "任务已加入队列，等待处理..."}
    redis_handler.set_job_status(job_id, initial_status)

    # Prepare the message for the Redis queue
    message = {
        "uid": uid,
        "job_id": job_id
    }
    
    # Push the job to a Redis list, which acts as our queue
    try:
        if redis_handler.redis_client:
            redis_handler.redis_client.lpush("analysis_queue", json.dumps(message))
            print(f"Pushed job {job_id} to Redis queue 'analysis_queue'")
            
            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={'code': 202, 'message': 'Analysis request accepted.', 'data': {'job_id': job_id}}
            )
        else:
            raise ConnectionError("Failed to connect to Redis.")
            
    except Exception as e:
        print(f"Failed to push job to Redis queue: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'code': 500, 'message': 'Failed to queue analysis request.'}
        )

@api_router.get("/job/status/{job_id}")
async def get_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Retrieves the status of a background job from Redis.
    """
    redis_handler = sql_use.SQL_redis()
    status_info = redis_handler.get_job_status(job_id)

    if status_info:
        return JSONResponse(status_code=200, content={'code': 200, 'message': 'success', 'data': status_info})
    else:
        return JSONResponse(status_code=404, content={'code': 404, 'message': 'Job not found or has expired.'})

@api_router.get("/history")
async def get_history(current_user: User = Depends(get_current_user)):
    history_data = database.get_history_by_user(current_user.id)
    return JSONResponse(
        status_code=200,
        content={'code': 200, 'message': 'success', 'data': history_data}
    )

# --- Mount Routers to the App ---
app.include_router(user_router)
app.include_router(api_router)