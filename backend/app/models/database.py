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
