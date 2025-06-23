from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
import json

import bilibili
import database
import sql_use
import comment_analysis

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

# --- API Routers ---
user_router = APIRouter(prefix="/user", tags=["user"])
api_router = APIRouter(prefix="/api", tags=["api"])

# --- User Authentication Routes ---
@user_router.post("/login")
def login_for_access_token(form_data: UserCreate):
    user_dict = database.get_user_by_username(username=form_data.username)
    if not user_dict or not isinstance(user_dict, dict) or 'password' not in user_dict or not verify_password(form_data.password, user_dict['password']):
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "Incorrect username or password"}
        )
    # Include both username and id in the token
    access_token = create_access_token(data={"sub": user_dict.get('username'), "id": user_dict.get('id')})
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

@api_router.get("/history")
async def get_history(current_user: User = Depends(get_current_user)):
    history_data = database.get_history_by_user(current_user.id)
    return JSONResponse(
        status_code=200,
        content={'code': 200, 'message': 'success', 'data': history_data}
    )

@api_router.get("/get_uids")
async def get_uids(current_user: User = Depends(get_current_user)):
    data = database.get_user_report()
    return {"code": 200, "data": data, "message": "成功"}

@api_router.post("/user/comments/{uid}")
async def get_user_comments(uid: int, current_user: User = Depends(get_current_user)):
    """
    直接获取用户评论并保存到数据库
    """
    try:
        print(f"用户 {current_user.username} 请求获取用户 {uid} 的评论")
        
        # 直接调用评论获取函数
        comments = bilibili.get_user_comments_simple(uid)
        
        if comments:
            print(f"成功获取 {len(comments)} 条评论，准备保存到数据库")
            # 保存到数据库
            success = database.save_user_comments(uid, current_user.username, comments)
            
            if success:
                print(f"评论数据已成功保存到数据库")
                return JSONResponse(
                    status_code=200,
                    content={
                        'code': 200, 
                        'message': 'success', 
                        'data': {
                            'uid': uid,
                            'comment_count': len(comments),
                            'comments': comments
                        }
                    }
                )
            else:
                print(f"保存到数据库失败")
                return JSONResponse(
                    status_code=500,
                    content={'code': 500, 'message': '保存到数据库失败', 'data': None}
                )
        else:
            print(f"未获取到用户 {uid} 的评论数据")
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据，可能是API访问限制或用户无评论', 'data': None}
            )
            
    except Exception as e:
        print(f"获取用户评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取评论失败: {str(e)}', 'data': None}
        )

@api_router.get("/user/comments/{uid}")
async def get_saved_user_comments(uid: int, current_user: User = Depends(get_current_user)):
    """
    从数据库获取已保存的用户评论数据
    """
    try:
        comments = database.get_user_comments(uid)
        
        if comments:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': comments}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据', 'data': None}
            )
            
    except Exception as e:
        print(f"获取保存的评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取评论失败: {str(e)}', 'data': None}
        )

@api_router.get("/user/comments/redis/{uid}")
async def get_user_comments_redis(uid: int, current_user: User = Depends(get_current_user)):
    """
    从Redis获取已保存的用户评论数据
    """
    try:
        from bilibili import get_user_comments_from_redis
        comments = get_user_comments_from_redis(uid)
        if comments:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': comments}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到该用户的评论数据', 'data': None}
            )
    except Exception as e:
        print(f"获取Redis评论失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取评论失败: {str(e)}', 'data': None}
        )

@api_router.post("/user/analyze/{uid}")
async def analyze_user_portrait(uid: int, current_user: User = Depends(get_current_user)):
    """
    分析用户评论，生成用户画像
    """
    bilibili.lpush(uid)
    
        
    try:
        from bilibili import get_user_analysis_from_redis
        result = get_user_analysis_from_redis(uid)
        
        if result:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': result}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到分析结果可能还在分析中', 'data': None}
            )
            
    except Exception as e:
        print(f"获取分析结果失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取失败: {str(e)}', 'data': None}
        )


"""
@api_router.post("/user/analyze/{uid}")
async def analyze_user_portrait(uid: int, current_user: User = Depends(get_current_user)):

    try:
        from bilibili import analyze_user_comments
        result = analyze_user_comments(uid)
        
        if "error" in result:
            return JSONResponse(
                status_code=400,
                content={'code': 400, 'message': result["error"], 'data': None}
            )
        
        return JSONResponse(
            status_code=200,
            content={'code': 200, 'message': '分析完成', 'data': result}
        )
        
    except Exception as e:
        print(f"用户画像分析失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'分析失败: {str(e)}', 'data': None}




"""
@api_router.get("/user/analysis/{uid}")
async def get_user_analysis(uid: int, current_user: User = Depends(get_current_user)):
    """
    获取用户画像分析结果
    """
    try:
        from bilibili import get_user_analysis_from_redis
        result = get_user_analysis_from_redis(uid)
        
        if result:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': result}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到分析结果', 'data': None}
            )
            
    except Exception as e:
        print(f"获取分析结果失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取失败: {str(e)}', 'data': None}
        )

# --- Background Task for Comment Analysis ---
def run_comment_analysis_task(bv_id: str, job_id: str):
    """
    The actual analysis function that runs in the background.
    """
    redis_handler = sql_use.SQL_redis()
    try:
        # 1. Update status: Fetching comments
        status_update = {"status": "Processing", "progress": 20, "details": f"正在获取视频 {bv_id} 的评论..."}
        redis_handler.set_job_status(job_id, status_update)
        
        comments = bilibili.select_by_BV(bv_id)
        if not comments:
            raise ValueError(f"未找到视频 {bv_id} 的评论数据，请检查BV号是否正确或稍后再试。")

        # 2. Update status: Analyzing comments
        status_update = {"status": "Processing", "progress": 60, "details": f"已获取 {len(comments)} 条评论，正在进行AI分析..."}
        redis_handler.set_job_status(job_id, status_update)

        analysis_result = comment_analysis.analyze_bv_comments(bv_id, comments)
        
        if "error" in analysis_result:
             raise Exception(analysis_result["error"])
        
        # 3. Update status: Completed
        status_update = {
            "status": "Completed", 
            "progress": 100, 
            "details": f"视频 {bv_id} 评论分析完成",
            "result": analysis_result
        }
        redis_handler.set_job_status(job_id, status_update)

    except Exception as e:
        error_message = f"评论分析任务失败: {e}"
        print(error_message)
        status_update = {"status": "Failed", "progress": 100, "details": error_message}
        redis_handler.set_job_status(job_id, status_update)
    finally:
        # Task finished, always release the lock
        lock_key = f"lock:analyze_bv:{bv_id}"
        redis_handler.release_lock(lock_key)
        print(f"Released lock for BV: {bv_id}")

# --- 评论分析相关API ---
@api_router.post("/comments/analyze/submit/{bv_id}")
async def submit_comment_analysis_job(bv_id: str, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Submits a comment analysis job. Checks for cached results first.
    If no cache, runs the job in the background and prevents duplicates with a lock.
    """
    # 1. Check for a cached result first
    cached_result = comment_analysis.get_bv_analysis(bv_id)
    if cached_result:
        print(f"Cache hit for analysis of BV: {bv_id}. Returning cached result.")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'code': 200, 'message': '已从缓存获取分析结果', 'data': cached_result}
        )
        
    # 2. If no cache, proceed with locking and job submission
    redis_handler = sql_use.SQL_redis()
    lock_key = f"lock:analyze_bv:{bv_id}"
    job_id = f"analyze_bv_{bv_id}_{uuid.uuid4().hex[:8]}"
    
    if not redis_handler.acquire_lock(lock_key, job_id, timeout=300):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={'code': 409, 'message': '该视频的分析任务已在进行中，请稍后再试。', 'data': None}
        )

    background_tasks.add_task(run_comment_analysis_task, bv_id, job_id)
    
    return JSONResponse(
        status_code=202, # HTTP 202 Accepted
        content={'code': 202, 'message': '分析任务已提交，将在后台进行处理。', 'data': {'job_id': job_id}}
    )

@api_router.get("/comments/analysis/{bv_id}")
async def get_comment_analysis(bv_id: str, current_user: User = Depends(get_current_user)):
    """
    获取指定BV视频的评论分析结果
    """
    try:
        from comment_analysis import get_bv_analysis
        result = get_bv_analysis(bv_id)
        
        if result:
            return JSONResponse(
                status_code=200,
                content={'code': 200, 'message': 'success', 'data': result}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={'code': 404, 'message': '未找到评论分析结果', 'data': None}
            )
            
    except Exception as e:
        print(f"获取评论分析结果失败: {e}")
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': f'获取失败: {str(e)}', 'data': None}
        )

# --- Mount Routers to the App ---
app.include_router(user_router)
app.include_router(api_router)