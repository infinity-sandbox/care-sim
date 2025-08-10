from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
import aiomysql
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from typing import Optional, Union, Any
from app.core.config import logger_settings, load_settings_from_db
logger = logger_settings.get_logger(__name__)
from app.schemas.client_schema import (UserOut,
                                       RegisterSchema, 
                                       TokenSchema, 
                                       TokenPayload, 
                                       PasswordResetRequest, 
                                       PasswordResetConfirm)
from app.models.user_model import User
from app.services.auth_service import AuthDatabaseService
from app.api.deps.user_deps import get_current_user, reuseable_oauth
from app.core.security import (get_password, 
                               verify_password, 
                               create_refresh_token, 
                               decode_jwt_token, 
                               create_access_token)
from app.services.user_service import UserService
from sqlalchemy.future import select

# Register and Login Endpoints
auth_router = APIRouter()

@auth_router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        # Perform an async query to fetch the user by email
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # SQL query to find user by email
            await cursor.execute(
                "SELECT * FROM auth_users WHERE email = %s",
                (form_data.username,)
            )
            user = await cursor.fetchone()  # Fetch the first matching user
        
        # if not user or not await verify_password(form_data.password, user['password']):
        #     raise HTTPException(status_code=400, detail="Invalid credentials")
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Return tokens if credentials are correct
        return {
            "access_token": await create_access_token(subject=user['id']),
            "refresh_token": await create_refresh_token(subject=user['id'])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        db.close()  # Close the connection after the operation
    
@auth_router.post("/register", response_model=dict)
async def register(user: RegisterSchema, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        async with db.cursor(aiomysql.DictCursor) as cursor:
            # Check if the user already exists by email or username
            await cursor.execute(
                "SELECT * FROM auth_users WHERE email = %s OR username = %s",
                (user.email, user.username)
            )
            user_exists = await cursor.fetchone()  # Fetch the first matching user

            if user_exists:
                raise HTTPException(status_code=400, detail="User already exists")

            # Insert new user into the database
            hashed_password = await get_password(user.password)  # Hash the password before saving
            await cursor.execute(
                "INSERT INTO auth_users (username, email, password, phone_number, address, security_question, security_answer) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user.username, user.email, hashed_password, user.phone_number, user.address, user.security_question, user.security_answer)
            )
            await db.commit()  # Commit the transaction

        return {"message": "User registered successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    finally:
        db.close()
        
@auth_router.post("/refresh", response_model=TokenSchema)
async def refresh_token(refresh_token: str = Body(...), db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        # Decode the JWT to get the token data
        token_data = await decode_jwt_token(refresh_token)
        
        # Use aiomysql to fetch the user based on the ID in the token
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM auth_users WHERE id = %s", 
                (token_data.sub,)
            )
            user = await cursor.fetchone()  # Fetch the user based on ID
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "access_token": await create_access_token(subject=user["id"]),
            "refresh_token": await create_refresh_token(subject=user["id"])
        }

    except Exception as e:
        logger.error(f"An unexpected error occurred during token refresh. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during token refresh"
        )
    
    finally:
        db.close()
        
@auth_router.post('/test-token', summary="Test if the access token is valid", response_model=UserOut)
async def test_token(user: User = Depends(get_current_user)):
    return user

@auth_router.post('/reset/email', summary="Send email for password reset", response_model=PasswordResetRequest)
async def reset_password_email(request: PasswordResetRequest, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        # Use aiomysql to fetch the user by email
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM auth_users WHERE email = %s", 
                (request.email,)
            )
            user = await cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a reset token
        reset_token = await create_access_token(subject=user["email"])
        reset_link = f"{logger_settings.FRONTEND_API_URL}/reset/password?token={reset_token}"

        # Send the reset email
        _status = await UserService.send_email(user["email"], reset_link)

        if _status:
            logger.debug("Password reset email sent!")
        else:
            logger.debug("Password reset email not sent!")

        return JSONResponse(
            content={"message": "Reset email sent successfully!"}
        )

    except Exception as e:
        logger.error(f"Error sending reset email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )
    
    finally:
        db.close()
        
@auth_router.post("/reset/password", summary="Reset password")
async def reset_password_confirm(request: PasswordResetConfirm, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        # Decode the reset token
        payload = jwt.decode(request.token, logger_settings.JWT_SECRET_KEY, algorithms=[logger_settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        # Fetch user by email using aiomysql
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM auth_users WHERE email = %s", (email,))
            user = await cursor.fetchone()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Update the user's password
        hashed_password = await get_password(request.new_password)
        
        # Update the password in the database
        async with db.cursor() as cursor:
            await cursor.execute(
                "UPDATE auth_users SET password = %s WHERE email = %s", 
                (hashed_password, email)
            )
            await db.commit()

        return {"message": "Password reset successfully!"}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {str(e)}")
    finally:
        db.close()
