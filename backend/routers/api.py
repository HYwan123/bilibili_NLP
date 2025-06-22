from .. import sql_use, database, auth, vector_db
from ..auth import User

api_router = APIRouter()

@api_router.post("/user/analysis/{uid}")
async def analysis(uid: int, current_user: User = Depends(get_current_user)):
    """
    Submits a user analysis job.
    """
    return JSONResponse(content=db_bilibili)