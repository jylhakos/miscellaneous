"""
Database Configuration Module
------------------------------
Establishes async SQLAlchemy engine and session management for TimescaleDB.
Supports high-performance time-series data operations.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Using async driver (asyncpg for PostgreSQL/TimescaleDB)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://trader_admin:SecureTradingPassword2026!@localhost:5432/power_db"
)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,  # Set to True for SQL query debugging
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Number of connections to maintain
    max_overflow=20  # Additional connections under load
)

# Session factory for database transactions
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass

async def get_db():
    """
    Dependency injection function for FastAPI routes.
    Provides a database session that automatically closes after use.
    
    Usage in FastAPI:
        @app.get("/data")
        async def get_data(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
