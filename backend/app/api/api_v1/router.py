from fastapi import APIRouter
# from app.api.api_v1.handlers import (chatbot,
#                                      environment)
from app.api.api_v1.handlers import care_sim_insight
from app.api.auth.jwt import auth_router

router = APIRouter()

router.include_router(auth_router, prefix='/auth', tags=["auth"])
router.include_router(care_sim_insight.insight_router, prefix='/insight', tags=["insight"])
# router.include_router(forecast.api, prefix='/varmax', tags=["varmax"])
# router.include_router(chatbot.chat_router, prefix='/chatbot', tags=["chatbot"])
# router.include_router(environment.env_router, prefix='/env', tags=["env"])
