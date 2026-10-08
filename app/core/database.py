"""Database connection and session lifecycle management."""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# Configure connection arguments for SQLite if applicable
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True,
)

# Enable foreign keys for SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()


import os

def init_db(auto_seed: bool = True) -> None:
    """Initialize database tables and ensure default demo users exist."""
    # Ensure directory exists for sqlite
    settings.ensure_directories()
    # Import all models to ensure they are registered with Base metadata
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    if not auto_seed or "test_" in settings.DATABASE_URL:
        return

    try:
        from app.models.user import User
        from app.models.medicine import Medicine

        session = SessionLocal()
        user_count = session.query(User).count()
        med_count = session.query(Medicine).count()
        session.close()

        if user_count == 0 or med_count == 0:
            from scripts.seed import seed_database
            seed_database(skip_init=True)
    except Exception as e:
        print(f"Auto-seed check: {e}")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session scope."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
