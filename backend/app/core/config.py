from typing import List, Any, Optional
import os, sys
from decouple import config
from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from pydantic import AnyHttpUrl
from logs.loggers.logger import logger_config
from utils.version import get_version_and_build
version, build = get_version_and_build()
import aiomysql
import os, sys
from fastapi import HTTPException
import json

class Settings(BaseModel):
    PROJECT_NAME: str = "care-sim"
    VERSION: str = version
    BUILD: str = build
    API_V1_STR: str = "/api/v1"
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY", cast=str)
    JWT_REFRESH_SECRET_KEY: str = config("JWT_REFRESH_SECRET_KEY", cast=str)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7   # 7 days
    # List[AnyHttpUrl] - backend cors origins type for validation
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    #
    ALLOWED_HTTP_REQUEST_METHODS: List[str] = ["*"]
    RESTRICTED_HTTP_REQUEST_METHODS: List[str] = ["*"]
    CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS: List[str] = ["*"]
    #
    FRONTEND_API_URL: str = config("FRONTEND_API_URL", cast=str)
    BACKEND_API_URL: str = config("BACKEND_API_URL", cast=str)
    MY_EMAIL: str = config("MY_EMAIL", cast=str)
    MY_EMAIL_PASSWORD: str = config("MY_EMAIL_PASSWORD", cast=str)
    EMAIL_APP_PASSWORD: str = config("EMAIL_APP_PASSWORD", cast=str)
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", cast=str)
    MODEL: str = config("MODEL", cast=str)
    #
    AUTH_DB_HOST: str = config("AUTH_DB_HOST", cast=str)
    AUTH_DB_PORT: str = config("AUTH_DB_PORT", cast=str)
    AUTH_DB_USER: str = config("AUTH_DB_USER", cast=str)
    AUTH_DB_PASSWORD: str = config("AUTH_DB_PASSWORD", cast=str)
    AUTH_DB: str = config("AUTH_DB", cast=str)
    #
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
    
    REDIS_HOST: str = "redis" # change to `redis` when in docker
    REDIS_PORT: int = 6379
    REQUESTS_PER_WINDOW: int = 30  # Max requests allowed in the time window
    TIME_WINDOW: int = 60  # Time window in seconds (e.g., 60 seconds or minute)
        
logger_settings = Settings()
