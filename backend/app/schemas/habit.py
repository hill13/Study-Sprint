"""
Habit Schemas - Define the shape of habit data for API requests/responses.

Schemas:
- HabitCreate: For creating a new habit
- HabitUpdate: For updating an existing habit (all fields optional)
- HabitResponse: What we return to the client
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


# =============================================================================
# SCHEMA 1: HabitCreate - For creating a new habit
# =============================================================================

# TODO: Create schema for habit creation
#
# Required fields:
#   - name: str - The habit name (e.g., "Study Math")
#
# Optional fields (have defaults in the model):
#   - description: Optional[str] = None
#   - subject_tag: Optional[str] = None
#   - goal_type: str = "daily"  (options: "daily", "frequency", "time")
#   - target_frequency: int = 7  (days per week)
#   - target_minutes: Optional[int] = None
#   - schedule_type: str = "daily"  (options: "daily", "weekdays", "custom")
#   - schedule_days: List[int] = []  (0=Monday, 6=Sunday)
#   - strict_streak: bool = False
#   - grace_days_per_month: int = 2

class HabitCreate(BaseModel):
    """Schema for creating a new habit."""
    name: str
    description: Optional[str] = None
    subject_tag: Optional[str] = None
    goal_type: str = "daily"
    target_frequency: int = 7
    target_minutes: Optional[int] = None
    schedule_type: str = "daily"
    schedule_days: List[int] = []
    strict_streak: bool = False
    grace_days_per_month: int = 2


# =============================================================================
# SCHEMA 2: HabitUpdate - For updating an existing habit
# =============================================================================

# TODO: Create schema for habit updates
#
# All fields are Optional because user might only update some fields
#
# Fields (all Optional):
#   - name: Optional[str] = None
#   - description: Optional[str] = None
#   - subject_tag: Optional[str] = None
#   - goal_type: Optional[str] = None
#   - target_frequency: Optional[int] = None
#   - target_minutes: Optional[int] = None
#   - schedule_type: Optional[str] = None
#   - schedule_days: Optional[List[int]] = None
#   - strict_streak: Optional[bool] = None
#   - grace_days_per_month: Optional[int] = None
#   - is_active: Optional[bool] = None

class HabitUpdate(BaseModel):
    """Schema for updating an existing habit. All fields optional."""
    name: Optional[str] = None
    description: Optional[str] = None
    subject_tag: Optional[str] = None
    goal_type: Optional[str] = None
    target_frequency: Optional[int] = None
    target_minutes: Optional[int] = None
    schedule_type: Optional[str] = None
    schedule_days: Optional[List[int]] = None
    strict_streak: Optional[bool] = None
    grace_days_per_month: Optional[int] = None
    is_active: Optional[bool] = None


# =============================================================================
# SCHEMA 3: HabitResponse - What we return to the client
# =============================================================================

# TODO: Create schema for habit responses
#
# Includes all fields from the database model:
#   - id: int
#   - user_id: int
#   - name: str
#   - description: Optional[str]
#   - subject_tag: Optional[str]
#   - goal_type: str
#   - target_frequency: int
#   - target_minutes: Optional[int]
#   - schedule_type: str
#   - schedule_days: List[int]
#   - strict_streak: bool
#   - grace_days_per_month: int
#   - is_active: bool
#   - created_at: datetime
#
# Don't forget: class Config with from_attributes = True

class HabitResponse(BaseModel):
    """Schema for habit data in API responses."""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    subject_tag: Optional[str]
    goal_type: str
    target_frequency: int
    target_minutes: Optional[int]
    schedule_type: str
    schedule_days: List[int]
    strict_streak: bool
    grace_days_per_month: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
