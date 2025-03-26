from fastapi import APIRouter
from .cv_router import router as cv_router

router = APIRouter()

# Include all sub-routers
router.include_router(cv_router, prefix="/cv", tags=["upload-cv"])