from fastapi import APIRouter
from app.api.api_v1.handlers import caresim
from app.api.auth.jwt import auth_router

router = APIRouter()

router.include_router(auth_router, prefix='/auth', tags=["auth"])
router.include_router(caresim.insight_router, prefix='/insight', tags=["insight"])
