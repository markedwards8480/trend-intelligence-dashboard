from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, NullPool
from app.config import settings
import os
import logging

logger = logging.getLogger(__name__)

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

is_sqlite = database_url.startswith("sqlite")

# Create database engine with proper connection pooling
if is_sqlite:
    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL: use connection pool (Railway free tier allows ~20 connections)
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections every 30 min
        pool_pre_ping=True,  # Verify connections are alive before using
        echo=False,
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


def run_migrations():
    """Add missing columns to existing tables (lightweight migration).

    SQLAlchemy's create_all() only creates new tables — it won't ALTER
    existing ones.  This function runs idempotent ALTER TABLE statements
    so new columns land in the production database.
    """
    from sqlalchemy import text, inspect

    inspector = inspect(engine)

    def _add_column_if_missing(table: str, column: str, col_type: str, default=None):
        cols = [c["name"] for c in inspector.get_columns(table)]
        if column not in cols:
            stmt = f'ALTER TABLE {table} ADD COLUMN {column} {col_type}'
            if default is not None:
                stmt += f' DEFAULT {default}'
            with engine.begin() as conn:
                conn.execute(text(stmt))
            logger.info(f"Added column {column} to {table}")

    # --- monitoring_targets additions ---
    _add_column_if_missing("monitoring_targets", "source_url", "VARCHAR(2048)")
    _add_column_if_missing("monitoring_targets", "source_name", "VARCHAR(255)")
    _add_column_if_missing("monitoring_targets", "target_demographics", "JSON")
    _add_column_if_missing("monitoring_targets", "frequency", "VARCHAR(50)", "'manual'")
    _add_column_if_missing("monitoring_targets", "trend_count", "INTEGER", "0")
    _add_column_if_missing("monitoring_targets", "last_scraped_at", "TIMESTAMPTZ")

    # --- trend_items additions ---
    _add_column_if_missing("trend_items", "demographic", "VARCHAR(50)")
    _add_column_if_missing("trend_items", "fabrications", "JSON")
    _add_column_if_missing("trend_items", "source_id", "INTEGER")

    # --- people table (new) ---
    # people table is created by create_tables() via SQLAlchemy models
    # No migrations needed for new tables
