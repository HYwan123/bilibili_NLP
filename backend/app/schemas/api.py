from pydantic import BaseModel

class CookieData(BaseModel):
    cookie: str