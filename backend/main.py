from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas.user import *
from schemas.api import *
from api import user, bilibili_api


#run
app = FastAPI()
#CORS - Allow all domains and IPs
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",   # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers to frontend
)

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(bilibili_api.router, prefix="/api", tags=["api"])
