from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas.user import *
from schemas.api import *
from api import user, bilibili_api


#run
app = FastAPI()
#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(bilibili_api.router, prefix="/api", tags=["api"])
