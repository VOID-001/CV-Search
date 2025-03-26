from fastapi import FastAPI
from middleware import logger
from routers.api_router import router as api_router
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import init_db

app = FastAPI(title=settings.app_name)

@app.on_event("startup")
async def startup_event():
    await init_db() 

# Middleware
app.middleware("http")(logger.log_requests)

# Routers
app.include_router(api_router)