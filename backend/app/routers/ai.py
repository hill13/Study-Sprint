"""
AI Router - Endpoint for generating AI-powered habit insights.

Endpoints:
  POST /ai/insights - Stream personalized habit analysis from Google Gemini
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.ai import stream_insights


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/insights")
def get_insights(
    db: Session = Depends(get_db),                      # opens a database connection for this request
    current_user: User = Depends(get_current_user)      # verifies JWT token + gives us the logged-in user
):
    """Stream AI-generated habit insights for the current user."""

    # event_stream is a nested function — defined here because it needs
    # access to db and current_user from the parent function
    #
    # It's also a generator (uses yield) — it produces chunks one at a time
    # instead of collecting everything and returning it all at once
    def event_stream():
        for chunk in stream_insights(db, current_user.id):  # current_user.id → whose habits to analyze
            yield f"data: {chunk}\n\n"                      # wrap in SSE format: "data: You're doing great\n\n"
                                                            # \n\n signals to the browser: "this chunk is complete"

    # StreamingResponse takes our generator and sends each yielded value
    # to the browser as it arrives — no waiting for the full response
    # media_type="text/event-stream" → tells the browser to expect SSE format
    return StreamingResponse(event_stream(), media_type="text/event-stream")
