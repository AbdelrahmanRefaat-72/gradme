"""
Central API v1 Router.
Aggregates all module-specific API sub-routers.
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.emails import router as emails_router
from app.api.v1.expected_rules import router as expected_rules_router
from app.api.v1.summaries import router as summaries_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.stats import router as stats_router
from app.api.v1.settings import router as settings_router

api_v1_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(emails_router)
api_v1_router.include_router(expected_rules_router)
api_v1_router.include_router(summaries_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(stats_router)
api_v1_router.include_router(settings_router)
