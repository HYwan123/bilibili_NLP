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

import bilibili
import database
import sql_use

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
        )

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

# --- Mount Routers to the App ---
app.include_router(user_router)
app.include_router(api_router)