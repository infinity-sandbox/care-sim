from typing import List, Optional
from pydantic import Field, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, Union, Any
Base = declarative_base()
from uuid import UUID

class AdminEnv(Base):
    """
        should have default value for all if it is not set (default user row: inside mysql db)
        # if one key is not set then it should be set to default value for that key from default user (not all keys)
        # if default user is not set then it should raise error
        # if it didn't fine all keys for a specific user use default user keys (all)

        @params that starts when the application starts
                if this are changed it needs redeployment
        - REQUESTS_PER_WINDOW = Column(Integer) #######
        - TIME_WINDOW = Column(Integer) #######
        - ALLOWED_HTTP_REQUEST_METHODS = Column(JSON) #######
        - RESTRICTED_HTTP_REQUEST_METHODS = Column(JSON) #######
        - CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS = Column(JSON) ######
        - BACKEND_CORS_ORIGINS = Column(JSON) #######
    """
    __tablename__ = "env_auth"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    DB_MS = Column(String(100))
    DB_USER = Column(String(100))
    DB_PASSWORD = Column(String(100))
    DB_HOST = Column(String(100))
    DB_PORT = Column(Integer)
    DB = Column(String(100))
    DB_TABLES = Column(JSON)
    DB_DRIVER= Column(String(100))
    MODEL = Column(String(500))
    OPENAI_API_KEY = Column(String(1000))
    WEAVIATE_URL = Column(String(1000))
    WEAVIATE_API_KEY = Column(String(1000))
    REDIS_HOST = Column(String(1000))
    REDIS_PORT = Column(Integer)
    MY_EMAIL = Column(String(500))
    MY_EMAIL_PASSWORD = Column(String(500))
    EMAIL_APP_PASSWORD = Column(String(500))
    FRONTEND_API_URL = Column(String(500))
    BACKEND_API_URL = Column(String(500))
    REQUESTS_PER_WINDOW = Column(Integer) 
    TIME_WINDOW = Column(Integer) 
    ALLOWED_HTTP_REQUEST_METHODS = Column(JSON) 
    RESTRICTED_HTTP_REQUEST_METHODS = Column(JSON) 
    CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS = Column(JSON) 
    BACKEND_CORS_ORIGINS = Column(JSON) 
    ACCESS_TOKEN_EXPIRE_MINUTES = Column(Integer)
    REFRESH_TOKEN_EXPIRE_MINUTES = Column(Integer)
    ALGORITHM = Column(String(100))
    JWT_SECRET_KEY = Column(String(1000))
    JWT_REFRESH_SECRET_KEY = Column(String(1000))
