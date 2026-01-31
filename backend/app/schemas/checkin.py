"""
CheckIn Schemas - Define the shape of check-in data for API requests/responses.

Schemas:
- CheckInCreate: For recording a check-in
- CheckInUpdate: For updating an existing check-in
- CheckInResponse: What we return to the client
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# =============================================================================
# SCHEMA 1: CheckInCreate - For recording a check-in
# =============================================================================

# TODO: Create schema for check-in creation
#
# Fields:
#   - habit_id: int - Which habit this is for
#   - check_in_date: date - The date of check-in (defaults to today)
#   - status: str = "completed" - Status (completed/missed/skipped)
#   - minutes_logged: Optional[int] = None - For time tracking
#   - notes: Optional[str] = None - Optional notes
#
# Note: check_in_date defaults to None, we'll set it to today in the endpoint

class CheckInCreate(BaseModel):
    """Schema for creating a check-in."""
    habit_id: int
    check_in_date: Optional[date] = None
    status: str = "completed"
    minutes_logged: Optional[int] = None
    notes: Optional[str] = None


# =============================================================================
# SCHEMA 2: CheckInUpdate - For updating a check-in
# =============================================================================

# TODO: Create schema for check-in updates
#
# All fields optional (user might only update some):
#   - status: Optional[str] = None
#   - minutes_logged: Optional[int] = None
#   - notes: Optional[str] = None
#
# Note: Can't change habit_id or date after creation

class CheckInUpdate(BaseModel):
    """Schema for updating an existing check-in."""
    status: Optional[str] = None
    minutes_logged: Optional[int] = None
    notes: Optional[str] = None


# =============================================================================
# SCHEMA 3: CheckInResponse - What we return to the client
# =============================================================================

# TODO: Create schema for check-in responses
#
# Fields:
#   - id: int
#   - habit_id: int
#   - check_in_date: date
#   - status: str
#   - minutes_logged: Optional[int]
#   - notes: Optional[str]
#   - created_at: datetime
#
# Don't forget: class Config with from_attributes = True

class CheckInResponse(BaseModel):
    """Schema for check-in data in API responses."""
    id: int
    habit_id: int
    check_in_date: date
    status: str
    minutes_logged: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
