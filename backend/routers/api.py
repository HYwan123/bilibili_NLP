from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from .. import sql_use, database, vector_db
from ..main import get_current_user, User
import uuid
import json

api_router = APIRouter()

@api_router.post("/user/analysis/{uid}")
async def analysis(uid: int, current_user: User = Depends(get_current_user)):
    """
    Submits a user analysis job.
    """
    # 这个函数现在在main.py中实现，这里可以删除或者重定向
    raise HTTPException(status_code=501, detail="This endpoint is implemented in main.py")