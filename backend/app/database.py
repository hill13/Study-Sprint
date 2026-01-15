"""
Database Connection Setup
-------------------------
This file configures SQLAlchemy to connect to your database.

HOW IT WORKS:
1. Engine: Creates the actual connection to the database
2. SessionLocal: A factory that creates new database sessions
3. Base: Parent class for all your models (User, Habit, etc.)
4. get_db: Dependency injection - gives each request its own session

WHY DEPENDENCY INJECTION?
- Each API request gets its own database session
- Session is automatically closed after the request (no leaks)
- Makes testing easier (you can swap in a test database)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# Create the database engine
# For SQLite, we need check_same_thread=False for FastAPI's async nature
# PostgreSQL doesn't need this
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}  # SQLite-specific
    )
else:
    engine = create_engine(settings.database_url)

# SessionLocal is a factory - calling it creates a new session
# autocommit=False: You must explicitly commit changes
# autoflush=False: Don't auto-sync with DB until you're ready
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All your models will inherit from this Base class
# This is how SQLAlchemy knows they're database tables
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session to route handlers.

    Usage in a route:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()

    The 'yield' keyword makes this a generator - the code after yield
    runs AFTER the route handler finishes (cleanup phase).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Always close the session, even if there's an error
