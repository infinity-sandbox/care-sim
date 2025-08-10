from typing import List
import os, sys
from decouple import config
from pydantic_settings import BaseSettings
from pydantic import BaseModel, ConfigDict
from pydantic import AnyHttpUrl
from logs.loggers.logger import logger_config
from utils.version import get_version_and_build
version, build = get_version_and_build()
from typing import Union, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from jose import jwt, JWTError
from pydantic import ValidationError


class Settings(BaseModel):
    def __init__(self, **data):
        super().__init__(**data)
        # Decode WEAVIATE_URL during initialization
        self.WEAVIATE_URL = self.decode(config("WEAVIATE_URL", cast=str))
        self.WEAVIATE_API_KEY = self.decode(config("WEAVIATE_API_KEY", cast=str))
        self.MODEL = self.decode(config("MODEL", cast=str))
        self.OPENAI_API_KEY = self.decode(config("OPENAI_API_KEY", cast=str))
        
    def encode(self, subject: Union[str, Any]) -> str:
        to_encode = {"sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.JWT_SECRET_KEY, self.ALGORITHM)
        return encoded_jwt

    def decode(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload['sub']
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token"
            )
            
    VERSION: str = version
    BUILD: str = build
    API_V1_STR: str = "/api/v1"
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY", cast=str)
    JWT_REFRESH_SECRET_KEY: str = config("JWT_REFRESH_SECRET_KEY", cast=str)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7   # 7 days
    #NOTE: backend cors origins only works for browser not fastapi/docs or curls access
    # BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
    #                                           #"https://akhil.applicare.io",
    #                                           "http://localhost:3000",
    #                                           #TODO: need to be removed before production
    #                                         ]
    # 
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    #
    # ALLOWED_HTTP_REQUEST_METHODS: List[str] = ["POST", "GET", "PUT"]
    # RESTRICTED_HTTP_REQUEST_METHODS: List[str] = ["GET", "PUT", "DELETE", "PATCH", "TRACE", "CONNECT", "OPTIONS"]
    # CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS: List[str] = ["PATCH", "TRACE", "CONNECT"]
    #
    # 
    ALLOWED_HTTP_REQUEST_METHODS: List[str] = ["*"]
    RESTRICTED_HTTP_REQUEST_METHODS: List[str] = ["*"]
    CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS: List[str] = ["*"]
    PROJECT_NAME: str = "applicare-ai"
    #
    FRONTEND_API_URL: str = config("FRONTEND_API_URL", cast=str)
    BACKEND_API_URL: str = config("BACKEND_API_URL", cast=str)
    #
    MY_EMAIL: str = config("MY_EMAIL", cast=str)
    MY_EMAIL_PASSWORD: str = config("MY_EMAIL_PASSWORD", cast=str)
    EMAIL_APP_PASSWORD: str = config("EMAIL_APP_PASSWORD", cast=str)
    #
    OPENAI_API_KEY: str = None
    MODEL: str = None
    '''
    Relational DB Config
    '''
    DB_MS: str = config("DB_MS", cast=str)
    DB_USER: str = config("DB_USER", cast=str)
    DB_PASSWORD: str = config("DB_PASSWORD", cast=str)
    DB_HOST: str = config("DB_HOST", cast=str)
    DB_PORT: int = config("DB_PORT", cast=int)
    DB: str = config("DB", cast=str)
    DB_TABLES: List[str] = [key.strip() for key in config("DB_TABLES").split(',')]
    #
    WEAVIATE_URL: str = None
    WEAVIATE_API_KEY: str = None
    #
    # AUTH_DB_HOST: str = config("AUTH_DB_HOST", cast=str)
    # AUTH_DB_PORT: str = config("AUTH_DB_PORT", cast=str)
    # AUTH_DB_USER: str = config("AUTH_DB_USER", cast=str)
    # AUTH_DB_PASSWORD: str = config("AUTH_DB_PASSWORD", cast=str)
    # AUTH_DB: str = config("AUTH_DB", cast=str)
    '''
    Directory Config
    '''
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__)) 
    PROMPT_DIR: str = os.path.join(os.path.abspath(os.path.join(BASE_DIR, "../")), "prompts/tx")
    LOG_DIR: str = os.path.join(os.path.abspath(os.path.join(BASE_DIR, "../../")), "logs")   
    ENV_PATH: str = os.path.join(os.path.abspath(os.path.join(BASE_DIR, "../../")), ".env")
    SQL_DIR: str = os.path.join(os.path.abspath(os.path.join(BASE_DIR, "../")), "sql/commands")
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=ENV_PATH
    )
    
    def get_logger(self, module_name: str):
        """Return a logger instance for the specified module name."""
        return logger_config(module=module_name)
    
    REDIS_HOST: str = "localhost" #TODO: change this to redis
    REDIS_PORT: int = 6379
    # Rate limit configuration
    REQUESTS_PER_WINDOW: int = 30  # Max requests allowed in the time window
    TIME_WINDOW: int = 60  # Time window in seconds (e.g., 60 seconds or minute)
    
settings = Settings()
