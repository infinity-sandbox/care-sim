from fastapi import APIRouter, HTTPException, Header, status
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Query
from app.core.config import load_settings_from_db, logger_settings
logger = logger_settings.get_logger(__name__)
from app.services.auth_service import AuthDatabaseService
from app.schemas.chatbot_schema import (
    GetQueryPayload, 
    GetRegeneratePayload, 
    GetReactionPayload
    )
from app.services.weaviate_service import (
    WeaviateService, 
    WeaviateQueryEngine, 
    SimpleWeaviateQueryEngine, 
    AdvancedWeaviateQueryEngine
    )
import aiomysql
from app.core.security import get_user_id

AdvancedWeaviateQueryEngine = AdvancedWeaviateQueryEngine()
SimpleWeaviateQueryEngine = SimpleWeaviateQueryEngine()

chat_router = APIRouter()

@chat_router.post("/query")
async def query(payload: GetQueryPayload, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        # decoded_usr = await get_user_id(payload.userId)
        decoded_usr = payload.userId  # Assuming userId is already decoded in the payload
        settings = await load_settings_from_db(decoded_usr, db=db)
        url = ""
        (system_msg, _userId, _messageId, _sessionId, _timestamp) = await AdvancedWeaviateQueryEngine.query(
            payload.query,
            decoded_usr,
            # payload.userId,
            payload.sessionId,
            url,
            settings
            )
        
        return JSONResponse(
            content={
                "system": system_msg,
                "userId": _userId,
                "messageId": _messageId,
                "sessionId": _sessionId,
                "timestamp": _timestamp
            }
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JSONResponse(
            content={
                "system": f"Unable to get response!",
                "userId": [],
                "messageId": [],
                "sessionId": [],
                "timestamp": [],
            },
            status_code=500
        )

@chat_router.post("/reaction")
async def reaction(reaction: GetReactionPayload, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    try:
        decoded_usr = await get_user_id(reaction.userId)
        (_userId, _sessionId, _messageId, 
         _timestamp, _rating, _feedbackText) = await AuthDatabaseService.add_reaction(
            decoded_usr,
            # reaction.userId,
            reaction.sessionId, 
            reaction.messageId, 
            reaction.rating, 
            reaction.feedbackText
            )
        return JSONResponse(
            content={
                "userId": _userId,
                "rating": _rating,
                "feedbackText": _feedbackText,
                "messageId": _messageId,
                "sessionId": _sessionId,
                "timestamp": _timestamp,
            }
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JSONResponse(
            content={
                "userId": f"Something went wrong! {str(e)}",
                "rating": [],
                "feedbackText": [],
                "messageId": [],
                "sessionId": [],
                "timestamp": [],
            },
            status_code=500
        )

@chat_router.post("/regenerate")
async def regenerate(regenerate: GetRegeneratePayload, db: aiomysql.Connection = Depends(AuthDatabaseService.get_db)):
    
    try:
        decoded_usr = await get_user_id(regenerate.userId)
        settings = await load_settings_from_db(decoded_usr, db=db)
        (system_msg, _userId, _, _sessionId, 
         _timestamp, _system_output, _feedbackText) = await AdvancedWeaviateQueryEngine.query_regenerator(
            regenerate.query, 
            decoded_usr, 
            # regenerate.userId,
            regenerate.sessionId, 
            regenerate.messageId,
            settings
            )
        return JSONResponse(
            content={
                "system": system_msg,
                "userId": _userId,
                "messageId": _,
                "sessionId": _sessionId,
                "timestamp": _timestamp,
                "system_output": _system_output,
                "feedbackText": _feedbackText,
            }
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JSONResponse(
            content={
                "system": f"Unable to get response!",
                "userId": [],
                "messageId": [],
                "sessionId": [],
                "timestamp": [],
                "system_output": [],
                "feedbackText": []
            },
            status_code=500
        )
