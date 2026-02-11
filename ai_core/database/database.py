from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from ai_core.core.config import settings

# Declarative base for ORM models
Base = declarative_base()

# Create SQLAlchemy engine using the configured database URL
# For SQLite, we need to disable check_same_thread
engine_kwargs = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    
engine = create_engine(settings.database_url, **engine_kwargs)

# Session factory for FastAPI dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a database session and ensure it closes after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
