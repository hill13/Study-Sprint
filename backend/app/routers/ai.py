"""
AI Router - Endpoint for generating AI-powered habit insights.

Endpoints:
  POST /ai/insights - Stream personalized habit analysis from Google Gemini
"""

import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.ai import stream_insights


router = APIRouter(prefix="/ai", tags=["AI"])

# In-memory rate limit store
# Stores the last request timestamp per user: { user_id: timestamp }
# Lives outside the function so it persists across requests (not reset each call)
# Limitation: resets on server restart, doesn't work across multiple servers
# Production alternative: Redis with a 60-second TTL
RATE_LIMIT_SECONDS = 60
last_request_times: dict[int, float] = {}


@router.post("/insights")
def get_insights(
    db: Session = Depends(get_db),                      # opens a database connection for this request
    current_user: User = Depends(get_current_user)      # verifies JWT token + gives us the logged-in user
):
    """Stream AI-generated habit insights for the current user."""

    # Rate limiting check
    # time.time() returns the current time as a float (seconds since 1970)
    # e.g. 1740001234.56
    now = time.time()
    last_request = last_request_times.get(current_user.id)  # None if this user has never requested

    if last_request and (now - last_request) < RATE_LIMIT_SECONDS:
        # How many seconds they still need to wait
        seconds_remaining = int(RATE_LIMIT_SECONDS - (now - last_request))  # → e.g. 42
        raise HTTPException(
            status_code=429,  # 429 = Too Many Requests (standard HTTP code for rate limiting)
            detail=f"Please wait {seconds_remaining} seconds before requesting again."
        )

    # Request is allowed — record this timestamp for next time
    last_request_times[current_user.id] = now

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
