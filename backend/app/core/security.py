from passlib.context import CryptContext
from typing import Union, Any
from jose import jwt
import os, hashlib
import asyncio
from app.core.config import Settings, logger_settings
logger = logger_settings.get_logger(__name__)
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, Union, Any
from app.schemas.client_schema import UserOut
from app.schemas.client_schema import TokenPayload
from datetime import datetime, timedelta, timezone
import base64
import json

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=logger_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, logger_settings.JWT_SECRET_KEY, logger_settings.ALGORITHM)
    return encoded_jwt

def _create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=logger_settings.REFRESH_TOKEN_EXPIRE_MINUTES)    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, logger_settings.JWT_REFRESH_SECRET_KEY, logger_settings.ALGORITHM)
    return encoded_jwt

def _get_password(password: str) -> str:
    return password_context.hash(password)

def _verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def _random_hash_generator(context: str = '', is_context: bool = False) -> str:
    if is_context:
        logger.info(f"Hashing context: {context}")
        return hashlib.md5(context.encode('utf-8') + os.urandom(32)).hexdigest()
    else:
        return hashlib.md5(os.urandom(32)).hexdigest()

def _decode_jwt_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, logger_settings.JWT_SECRET_KEY, algorithms=[logger_settings.ALGORITHM])
        return TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )

# Async function for creating access token
async def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    return await asyncio.to_thread(_create_access_token, subject, expires_delta)

# Async function for creating refresh token
async def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    return await asyncio.to_thread(_create_refresh_token, subject, expires_delta)

# Async function for hashing a password
async def get_password(password: str) -> str:
    return await asyncio.to_thread(_get_password, password)

# Async function for verifying password
async def verify_password(password: str, hashed_pass: str) -> bool:
    return await asyncio.to_thread(_verify_password, password, hashed_pass)

# Async function for generating a random hash
async def random_hash_generator(context: str = '', is_context: bool = False) -> str:
    return await asyncio.to_thread(_random_hash_generator, context, is_context)

# Async function for decoding a JWT token
async def decode_jwt_token(token: str) -> TokenPayload:
    return await asyncio.to_thread(_decode_jwt_token, token)

async def get_user_id(token: str) -> str:
    # Decode without verification
    header = jwt.get_unverified_header(token)
    claims = jwt.get_unverified_claims(token)
    logger.debug(f"Header: {header}\nClaims: {claims}\nUser: {claims['sub']}")
    return claims['sub']
