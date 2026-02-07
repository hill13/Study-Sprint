"""
Analytics Router - Endpoints for habit statistics and charts.

Endpoints:
  GET /analytics/overview - Get all analytics data for the dashboard
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.analytics import get_overview


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all analytics data for the current user."""
    return get_overview(db, current_user.id)
