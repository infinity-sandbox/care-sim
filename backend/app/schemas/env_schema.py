from typing import List, Optional
from pydantic import Field, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, Union, Any
Base = declarative_base()
from uuid import UUID

class AdminEnvPayload(BaseModel):
    # email: EmailStr
    email: str
    email_user: Optional[str] = None
    DB_MS: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB: Optional[str] = None
    DB_TABLES: Optional[List[str]] = None
    DB_DRIVER: Optional[str] = None
    MODEL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    WEAVIATE_URL: Optional[str] = None
    WEAVIATE_API_KEY: Optional[str] = None
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    MY_EMAIL: Optional[EmailStr] = None
    MY_EMAIL_PASSWORD: Optional[str] = None
    EMAIL_APP_PASSWORD: Optional[str] = None
    FRONTEND_API_URL: Optional[str] = None
    BACKEND_API_URL: Optional[str] = None
    REQUESTS_PER_WINDOW: Optional[int] = None
    TIME_WINDOW: Optional[int] = None
    ALLOWED_HTTP_REQUEST_METHODS: Optional[List[str]] = None
    RESTRICTED_HTTP_REQUEST_METHODS: Optional[List[str]] = None
    CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS: Optional[List[str]] = None
    BACKEND_CORS_ORIGINS: Optional[List[str]] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    REFRESH_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    ALGORITHM: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    JWT_REFRESH_SECRET_KEY: Optional[str] = None

class UserEnvPayload(BaseModel):
    # email: EmailStr
    email: str
    DB_MS: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB: Optional[str] = None
    DB_TABLES: Optional[List[str]] = None

class UserEmail(BaseModel):
    # email: EmailStr
    email: str
