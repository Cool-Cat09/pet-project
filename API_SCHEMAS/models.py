from pydantic import BaseModel, HttpUrl, EmailStr
from datetime import datetime


#Pydantic models to annotations 

class CreatingItem(BaseModel):
    url: HttpUrl 
    name: str 
    need_price: int 
    shop: str 
    
class UpdateItem(BaseModel):
    url: HttpUrl | None = None
    name: str | None = None
    need_price: int | None = None
    shop: str | None = None

class CreatingUser(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str

class Creating_Session_Cookie(BaseModel):
    session_id: str
    expires_at: datetime
    user_id: int