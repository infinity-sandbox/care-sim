import os, sys
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from utils.console.banner import run_banner
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import logger_settings, Settings
logger = logger_settings.get_logger(__name__)
import asyncio
from app.models.user_model import User
from app.models.env_model import AdminEnv
from app.api.api_v1.router import router
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from app.services.auth_service import AuthDatabaseService
import uvicorn
import time
import redis.asyncio as redis
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware

# Create and configure FastAPI app
def create_app():
    app = FastAPI(
        title=logger_settings.PROJECT_NAME,
        openapi_url=f'{logger_settings.API_V1_STR}/openapi.json',
    )
    return app

async def redis_client():
    try:
        # Create the Redis client
        client = redis.from_url(
            f"redis://{logger_settings.REDIS_HOST}:{logger_settings.REDIS_PORT}",
            decode_responses=True,
        )
        # Test the connection
        pong = await client.ping()
        return client
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        raise
    
# Helper function to get the current time in seconds
def current_time():
    return int(time.time())

# Rate limiting function
async def rate_limit(user_id: str):
    # The Redis key for the user's request timestamps
    redis_clt = await redis_client()
    redis_key = f"user:{user_id}:requests"

    # Get the current time
    now = current_time()

    # Remove any timestamps that are older than the time window
    await redis_clt.ltrim(redis_key, 0, logger_settings.REQUESTS_PER_WINDOW - 1)

    # Check how many requests the user has made in the current window
    requests = await redis_clt.lrange(redis_key, 0, -1)

    # If the user has exceeded the limit, raise an error
    if len(requests) >= logger_settings.REQUESTS_PER_WINDOW:
        logger.error(f"User '{user_id}' has exceeded the rate limit.")
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")

    # Add the current timestamp to the list of requests
    await redis_clt.lpush(redis_key, now)

    # Set an expiration time on the list key to ensure old timestamps are automatically removed
    await redis_clt.expire(redis_key, logger_settings.TIME_WINDOW)
    
# Create a custom middleware to apply rate limit to every request
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = str(request.client.host)  # You can use IP or any identifier

        # Apply rate limiting before processing the request
        await rate_limit(user_id)

        # Proceed to the next step (the actual route handler)
        response = await call_next(request)
        return response
    
# Function for banner and directory initialization
def init_paths():
    # Get the absolute path of the current file
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))    
    BASE_DIR = os.path.join(os.path.abspath(os.path.join(CURRENT_DIR, "../")), "utils")
    if not os.path.exists(BASE_DIR):
        BASE_DIR = '.'

    # Set the distribution directory based on the operating system
    if sys.platform in ["darwin", "win32", "linux", "linux2"]:
        VITE_DIST_DIR: str = os.path.join(BASE_DIR, "dist")  # Reference the dist folder under utils
    else:
        raise Exception("Unsupported operating system")
    return VITE_DIST_DIR

# Mount static files if available
def mount_static_files(app, vite_dist_dir):
    static_dir = f"{vite_dist_dir}/static"
    index_html_path = f"{vite_dist_dir}/index.html"
    
    if os.path.exists(vite_dist_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    return index_html_path

# Serve frontend
async def serve_frontend(index_html_path):
    # if os.path.exists(index_html_path):
    #     return FileResponse(index_html_path)
    return JSONResponse(
            content={
                "message": "care simulator backend api. welcome to the jungle!"
            },
            status_code=404
        )

# Serve favicon if available
async def get_favicon(vite_dist_dir):
    favicon_path = f"{vite_dist_dir}/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(content={"message": "Favicon not found."}, status_code=404)

# Middleware to restrict certain HTTP methods from untrusted origins
async def restrict_methods_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    method = request.method

    if origin not in logger_settings.BACKEND_CORS_ORIGINS:
        if method in logger_settings.RESTRICTED_HTTP_REQUEST_METHODS:
            logger.error(f"Untrusted origin '{origin}' attempted to use method '{method}'.")
            raise HTTPException(status_code=403, 
                                detail=f"Method {method} is not allowed for untrusted origins.")
    
    response = await call_next(request)
    return response

async def auth_db_startup():
    """
    Initialize and verify the authentication database with required tables.
    """
    is_connected = await AuthDatabaseService.ping_database()
    if not is_connected:
        logger.error("Failed to connect to the database!")
        raise RuntimeError("Database connection failed.")
    
    # await AuthDatabaseService.ensure_env_table_exists()
    # await AuthDatabaseService.ensure_cache_schema_exists()
    await AuthDatabaseService.ensure_auth_table_exists()

    logger.info("Successfully connected to the authentication database.")
        
async def auth_db_shutdown():
    try:
        await AuthDatabaseService.auth_shutdown()
        logger.info(f"Successfully closed authentication database connection.")
    except Exception as e:
        logger.error(f"Error closing authentication database connection: {e}")
    
async def redis_startup(redis_clt):
    try:
        await redis_clt.ping()
        logger.info("Successfully connected to Redis.")
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
            
async def redis_shutdown(redis_clt):
    try:
        await redis_clt.aclose()
        logger.info("Successfully closed Redis connection")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")
    
def run_app():
    app = create_app()

    # Run banner
    run_banner(logger_settings.VERSION, logger_settings.BUILD)

    # Initialize paths and static files
    vite_dist_dir = init_paths()
    index_html_path = mount_static_files(app, vite_dist_dir)

    # Add middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=logger_settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=logger_settings.ALLOWED_HTTP_REQUEST_METHODS,
        allow_headers=["*"]
    )
    
    # Register the middleware for restricted methods
    # app.middleware("http")(restrict_methods_middleware)
    
    # Add the rate-limiting middleware
    # app.add_middleware(RateLimitMiddleware)

    # Route setup  
    @app.get("/", response_class=HTMLResponse)
    async def root():
        return await serve_frontend(index_html_path)

    @app.get("/favicon.ico")
    async def get_favicon_route():
        return await get_favicon(vite_dist_dir)

    # Register the router for API routes
    app.include_router(router, prefix=logger_settings.API_V1_STR)

    async def redis_client_support() -> redis.Redis:
        redis_clt = await redis_client()
        return redis_clt
        
    # Event for app initialization
    @app.on_event("startup")
    async def on_startup():
        logger.info("Starting up...")
        # redis_clt = await redis_client_support()
        await asyncio.gather(
            # redis_startup(redis_clt),
            auth_db_startup(),
            AuthDatabaseService.ensure_user_input_insight_tables_exists()
        )
        
    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("Shutting down...")
        # redis_clt = await redis_client_support()
        await asyncio.gather(
            # redis_shutdown(redis_clt),
            auth_db_shutdown()
        )
    return app

# Run the FastAPI app
app = run_app()
