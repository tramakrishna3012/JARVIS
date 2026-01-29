"""
Database Configuration and Session Management
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Create async engine
# Create async engine
# Ensure we use asyncpg driver
# Aggressive replacement to handle any variation of postgres://
db_url = str(settings.DATABASE_URL).strip()
db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
db_url = db_url.replace("postgres://", "postgresql+asyncpg://")

print("DEBUG: Creating engine with statement_cache_size=0 and NullPool (VERSION 2)")
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    poolclass=NullPool,
    pool_pre_ping=False,
    connect_args={"statement_cache_size": 0} # Required for Supabase Transaction Pooler
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import all models to register them
        from app.models import user, profile, job, resume, application, referral, email
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
