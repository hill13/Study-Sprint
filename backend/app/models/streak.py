"""
Streak Model
------------
Tracks streak statistics for each habit.

WHY A SEPARATE TABLE?
Instead of calculating streaks on every request (expensive),
we store the current state and update it when check-ins happen.

STREAK STATUS (from your spec):
- 'safe': On track, no missed days recently
- 'at_risk': Missed today but streak not broken yet
- 'grace_used': Used a grace day, still alive
- 'broken': Streak has been reset

This enables the motivational UI that keeps users engaged!
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Streak(Base):
    __tablename__ = "streaks"

    id = Column(Integer, primary_key=True, index=True)

    # One streak record per habit (one-to-one relationship)
    habit_id = Column(Integer, ForeignKey("habits.id"), unique=True, nullable=False)

    # Core streak data
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)

    # When did the current streak start?
    streak_start_date = Column(Date, nullable=True)

    # Grace day tracking for the current month
    grace_days_used = Column(Integer, default=0)
    grace_days_reset_date = Column(Date, nullable=True)  # When to reset grace counter

    # Current status for UI display
    # 'safe', 'at_risk', 'grace_used', 'broken'
    status = Column(String, default="safe")

    # Last activity tracking
    last_check_in_date = Column(Date, nullable=True)
    last_missed_date = Column(Date, nullable=True)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship
    habit = relationship("Habit", back_populates="streak")

    def __repr__(self):
        return f"<Streak habit={self.habit_id} current={self.current_streak}>"
