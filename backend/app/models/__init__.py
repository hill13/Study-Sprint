"""
Database Models
---------------
Import all models here so they can be imported from one place:
    from app.models import User, Habit, CheckIn, Streak

This also ensures all models are loaded when we create tables.
"""

from app.models.user import User
from app.models.habit import Habit
from app.models.checkin import CheckIn
from app.models.streak import Streak

# This list is useful for debugging - see all models at once
__all__ = ["User", "Habit", "CheckIn", "Streak"]
