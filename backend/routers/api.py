from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import sql_use
import database
import uuid
import json

api_router = APIRouter()

@api_router.post("/user/analysis/{uid}")
async def analysis(uid: int, current_user=None):
    """
    Submits a user analysis job.
    """
    # 这个函数现在在main.py中实现，这里可以删除或者重定向
    raise HTTPException(status_code=501, detail="This endpoint is implemented in main.py")