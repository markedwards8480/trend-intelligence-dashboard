from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings
import os

# Determine database URL - use SQLite fallback for local development
database_url = settings.DATABASE_URL

# Fix common Railway/Heroku issue: postgres:// → postgresql://
# SQLAlchemy 2.0+ requires the full "postgresql://" scheme
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# If using default PostgreSQL URL and it looks like a placeholder/not configured,
# fallback to SQLite for local development
if database_url.startswith("postgresql://postgres:postgres@localhost") and not os.getenv("DATABASE_URL"):
    database_url = "sqlite:///./trend_dashboard.db"

# Create database engine
engine = create_engine(
    database_url,
    poolclass=NullPool if not database_url.startswith("sqlite") else None,
    echo=False,
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
