from typing import List, Optional
from pydantic import Field, EmailStr
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, Union, Any
from uuid import UUID
    
class RegisterSchema(BaseModel):
    username: str
    # email: EmailStr
    email: str
    password: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    security_question: Optional[str] = None
    security_answer: Optional[str] = None
    
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str
    exp: int

# Pydantic Schemas
class PasswordResetRequest(BaseModel):
    # email: EmailStr
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
class UserOut(BaseModel):
    id: int
    username: str
    # email: EmailStr
    email: str