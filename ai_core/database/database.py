from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from ai_core.core.config import settings

# Declarative base for ORM models
Base = declarative_base()

# Create SQLAlchemy engine using the configured database URL
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Session factory for FastAPI dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a database session and ensure it closes after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
