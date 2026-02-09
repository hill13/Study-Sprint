"""
FastAPI Application Entry Point
-------------------------------
This is where your API starts. When you run `uvicorn app.main:app`,
Python loads this file and uses the `app` object to handle requests.

KEY CONCEPTS:
- FastAPI() creates your application instance
- @app.get/post/etc. decorators define endpoints
- Middleware runs on every request (like CORS handling)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import User, Habit, CheckIn, Streak  # Import models to register them

# Create database tables (for development)
# In production, you'd use Alembic migrations instead
Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI(
    title="StudySprint API",
    description="Backend API for the StudySprint habit tracker",
    version="0.1.0",
)

# CORS Middleware - IMPORTANT for frontend-backend communication
# Without this, your React app can't talk to your API (browser security)
app.add_middleware(
    CORSMiddleware,
    # In development, allow your frontend origin
    # In production, replace with your actual frontend URL
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Common React dev port
        "https://studysprint.vercel.app",  # Production frontend
    ],
    allow_origin_regex=r"https://study-sprint.*\.vercel\.app",  # Preview deployments
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)


# Health check endpoint - useful for deployment platforms
# They ping this to verify your server is running
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "StudySprint API is running"}


# Root endpoint - basic info about the API
@app.get("/")
def root():
    return {
        "app": "StudySprint",
        "version": "0.1.0",
        "docs": "/docs",  # FastAPI auto-generates interactive docs here
    }


# Register routers
from app.routers import auth, habits, checkins, analytics
app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(checkins.router)
app.include_router(analytics.router)
