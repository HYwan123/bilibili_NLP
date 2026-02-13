from pydantic import BaseModel
from typing import List, Optional


class CookieData(BaseModel):
    cookie: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "kimi-k2"


class ChatResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None
