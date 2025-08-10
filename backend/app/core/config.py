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
    PROJECT_NAME: str = "applicare-ai"
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
    DB_MS: str = None
    DB_USER: str = None
    DB_PASSWORD: str = None
    DB_HOST: str = None
    DB_PORT: int = None
    DB: str = None
    DB_TABLES: List[str] = None 
    # WEAVIATE_URL: str = config("WEAVIATE_URL", cast=str)
    # WEAVIATE_API_KEY: str = config("WEAVIATE_API_KEY", cast=str)
    AUTH_DB_HOST: str = config("AUTH_DB_HOST", cast=str)
    AUTH_DB_PORT: str = config("AUTH_DB_PORT", cast=str)
    AUTH_DB_USER: str = config("AUTH_DB_USER", cast=str)
    AUTH_DB_PASSWORD: str = config("AUTH_DB_PASSWORD", cast=str)
    AUTH_DB: str = config("AUTH_DB", cast=str)
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
    
    REDIS_HOST: str = "localhost" # change to `redis` when in docker
    REDIS_PORT: int = 6379
    REQUESTS_PER_WINDOW: int = 30  # Max requests allowed in the time window
    TIME_WINDOW: int = 60  # Time window in seconds (e.g., 60 seconds or minute)
        
logger_settings = Settings()
logger = logger_settings.get_logger(__name__)

async def load_settings_from_db(email: str, db: aiomysql.Connection) -> Settings:
    """
    Load settings dynamically from the database for a specific user.
    If the specific user's values are missing, fallback to default user values.

    :param email: The email of the user whose settings are to be loaded.
    :param db: Database session object.
    :return: A Settings object populated with data from the database.
    """
    # Ensure db is an instance of Session
    logger.debug(f"Fetching environments for user {email} starts...")

    if not isinstance(db, aiomysql.Connection):
        raise ValueError("Expected 'db' to be an instance of SQLAlchemy AsyncSession")
    def parse_db_tables(db_tables: str, fallback: list) -> list:
        """
        Safely parse DB_TABLES if it's a string or use the fallback list.
        """
        if isinstance(db_tables, str):
            try:
                return json.loads(db_tables)  # Attempt to parse as JSON string
            except json.JSONDecodeError:
                # Log error if the string is not valid JSON and return fallback
                logger.error(f"Error parsing DB_TABLES JSON: {db_tables}")
                return fallback
        return db_tables if isinstance(db_tables, list) else fallback
    try:
        # Query for the specific user
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM env_auth WHERE email = %s", (email,)
            )
            user_env = await cursor.fetchone()  # Get the first matching result
            if user_env:
                logger.debug(f"TODEL: User environment found for {email}")
                logger.debug(f"TODEL:  {user_env}")
                # Ensure correct types and map to settings
                # Helper function to safely parse a JSON string into a list
                
                user_env = {
                    'DB_MS': user_env.get('DB_MS', logger_settings.DB_MS),
                    'DB_USER': user_env.get('DB_USER', logger_settings.DB_USER),
                    'DB_PASSWORD': user_env.get('DB_PASSWORD', logger_settings.DB_PASSWORD),
                    'DB_HOST': user_env.get('DB_HOST', logger_settings.DB_HOST),
                    'DB_PORT': int(user_env.get('DB_PORT', logger_settings.DB_PORT)) if user_env.get('DB_PORT') else logger_settings.DB_PORT,
                    'DB': user_env.get('DB', logger_settings.DB),
                    'DB_TABLES': parse_db_tables(
                        user_env.get('DB_TABLES', logger_settings.DB_TABLES),
                        logger_settings.DB_TABLES  # Default fallback if it's invalid
                    ),
                }
                return Settings(**user_env)  # Convert the dictionary to a Settings object
            else:
                # Query for the default user as a fallback
                await cursor.execute(
                    "SELECT * FROM env_auth WHERE email = %s", ("default@user.com",)
                )
                default_env = await cursor.fetchone()  # Get the first matching result
                
                if not default_env:
                    logger.debug("Default user environment not found.")
                    raise ValueError("Default user configuration (default@user.com) is missing in the database.")
                logger.debug("Default user environment found.")
                default_env = {
                    'DB_MS': default_env.get('DB_MS', logger_settings.DB_MS),
                    'DB_USER': default_env.get('DB_USER', logger_settings.DB_USER),
                    'DB_PASSWORD': default_env.get('DB_PASSWORD', logger_settings.DB_PASSWORD),
                    'DB_HOST': default_env.get('DB_HOST', logger_settings.DB_HOST),
                    'DB_PORT': int(default_env.get('DB_PORT', logger_settings.DB_PORT)) if default_env.get('DB_PORT') else logger_settings.DB_PORT,
                    'DB': default_env.get('DB', logger_settings.DB),
                    'DB_TABLES': parse_db_tables(
                        default_env.get('DB_TABLES', logger_settings.DB_TABLES),
                        logger_settings.DB_TABLES  # Default fallback if it's invalid
                    ),
                }
                return Settings(**default_env)  # Convert the dictionary to a Settings object

    except Exception as e:
        # Handle any exceptions that occur during the database queries
        raise HTTPException(status_code=500, detail=f"Error retrieving user environment: {e}")
    
    # Function to get value or fallback
    def get_value(key: str) -> Any:
        """
        Fetch the value from the user's environment settings if available,
        else fallback to the default environment settings.
        """
        user_value = getattr(user_env, key, None) if user_env else None
        default_value = getattr(default_env, key, None)
        logger.debug(f"Fetched \n\n{key}:{user_value if user_value not in [None, "", [], [""], 0] else default_value}")
        return user_value if user_value not in [None, "", [], [""], 0] else default_value
    
    # Dynamically populate the settings
    settings = Settings(
        PROJECT_NAME=logger_settings.PROJECT_NAME,  # Static default
        VERSION=logger_settings.VERSION,
        BUILD=logger_settings.BUILD,
        API_V1_STR=logger_settings.API_V1_STR,
        JWT_SECRET_KEY=logger_settings.JWT_SECRET_KEY,
        JWT_REFRESH_SECRET_KEY=logger_settings.JWT_REFRESH_SECRET_KEY,
        ALGORITHM=logger_settings.ALGORITHM,
        ACCESS_TOKEN_EXPIRE_MINUTES=logger_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        REFRESH_TOKEN_EXPIRE_MINUTES=logger_settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        BACKEND_CORS_ORIGINS=logger_settings.BACKEND_CORS_ORIGINS,
        ALLOWED_HTTP_REQUEST_METHODS=logger_settings.ALLOWED_HTTP_REQUEST_METHODS,
        RESTRICTED_HTTP_REQUEST_METHODS=logger_settings.RESTRICTED_HTTP_REQUEST_METHODS,
        CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS=logger_settings.CRITICAL_RESTRICTED_HTTP_REQUEST_METHODS,
        FRONTEND_API_URL=logger_settings.FRONTEND_API_URL,
        BACKEND_API_URL=logger_settings.BACKEND_API_URL,
        MY_EMAIL=logger_settings.MY_EMAIL,
        MY_EMAIL_PASSWORD=logger_settings.MY_EMAIL_PASSWORD,
        EMAIL_APP_PASSWORD=logger_settings.EMAIL_APP_PASSWORD,
        OPENAI_API_KEY=logger_settings.OPENAI_API_KEY,
        MODEL=logger_settings.MODEL,
        DB_MS=get_value("DB_MS"),
        DB_USER=get_value("DB_USER"),
        DB_PASSWORD=get_value("DB_PASSWORD"),
        DB_HOST=get_value("DB_HOST"),
        DB_PORT=get_value("DB_PORT"),
        DB=get_value("DB"),
        DB_TABLES=get_value("DB_TABLES"),
        # WEAVIATE_URL=logger_settings.WEAVIATE_URL,
        # WEAVIATE_API_KEY=logger_settings.WEAVIATE_API_KEY,
        AUTH_DB_HOST=logger_settings.AUTH_DB_HOST,
        AUTH_DB_PORT=logger_settings.AUTH_DB_PORT,
        AUTH_DB_USER=logger_settings.AUTH_DB_USER,
        AUTH_DB_PASSWORD=logger_settings.AUTH_DB_PASSWORD,
        AUTH_DB=logger_settings.AUTH_DB,
        BASE_DIR=logger_settings.BASE_DIR,  # Static value
        PROMPT_DIR=logger_settings.PROMPT_DIR,
        LOG_DIR=logger_settings.LOG_DIR,
        ENV_PATH=logger_settings.ENV_PATH,
        SQL_DIR=logger_settings.SQL_DIR,
        REDIS_HOST=logger_settings.REDIS_HOST,
        REDIS_PORT=logger_settings.REDIS_PORT,
        REQUESTS_PER_WINDOW=logger_settings.REQUESTS_PER_WINDOW,
        TIME_WINDOW=logger_settings.TIME_WINDOW,
    )

    return settings
