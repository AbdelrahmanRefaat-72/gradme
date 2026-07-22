"""
FastAPI Main Application Entrypoint for Smart Email Guardian.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.database.session import engine, get_db
from app.database.base import Base
from app.api.v1.router import api_v1_router
import app.models  # Register all models for SQLAlchemy Base.metadata creation

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Cybersecurity Email Security Guardian API with Rule-Based Phishing Engine, Expected Email Tracking, and AI Summarization.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include API v1 Router
app.include_router(api_v1_router)

# CORS Configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Spawns the background task to listen for Telegram /start commands.
    """
    import asyncio
    from app.services.notifications.telegram_service import start_telegram_listener
    asyncio.create_task(start_telegram_listener())


@app.get("/health", tags=["Health"])
def health_check():
    """
    System health check endpoint.
    """
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
