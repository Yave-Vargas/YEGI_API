from fastapi import APIRouter
from app.api.endpoints import models, summarizer, extract

api_router = APIRouter()

api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(summarizer.router, prefix="/summarizer", tags=["Summarizer"])
api_router.include_router(extract.router, prefix="/extract", tags=["Extract"])
