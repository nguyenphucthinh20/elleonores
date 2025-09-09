from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username : str
    
class UserUpdate(BaseModel):
    password: str
    username : str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
