from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)  # This will print the URL to verify it's correct

# Verify that the URL is not None and properly formatted
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in the environment variables.")

# Use asynchronous engine for async capabilities with PostgreSQL
try:
    engine = create_async_engine(DATABASE_URL, echo=True)
except Exception as e:
    print("Failed to create async engine:", e)
    raise

# Asynchronous session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# You need to import Base from models to create all tables properly
from database.models import Base

async def init_db():
    # Create tables if they don't exist in the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependency provider for database sessions
async def get_db():
    async with SessionLocal() as session:
        yield session