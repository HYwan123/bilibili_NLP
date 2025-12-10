from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.user import *
from app.schemas.api import *
from app.api import user, bilibili_api
from app.database.mysql_exceptions import register_exception_handlers
import os

# Initialize app
app = FastAPI(title="Bilibili NLP API", version="1.0.0")

# CORS - Allow specific origins only (more secure)
# ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",   # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers to frontend
)

# Include routers
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(bilibili_api.router, prefix="/api", tags=["api"])

# Register exception handlers
register_exception_handlers(app)
