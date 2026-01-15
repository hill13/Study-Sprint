"""
CheckIn Model
-------------
Records a single day's completion status for a habit.

KEY DESIGN DECISIONS:
1. One check-in per habit per day (enforced by unique constraint)
2. Status can be 'completed', 'missed', or 'skipped' (for flexibility)
3. Optional notes let users add context ("Studied chapter 3")
4. Minutes tracked for time-based goals
5. created_at allows "undo within 24 hours" feature
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CheckIn(Base):
    __tablename__ = "check_ins"

    id = Column(Integer, primary_key=True, index=True)

    # Which habit this check-in belongs to
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)

    # The date of the check-in (just the date, no time)
    # Using Date type prevents timezone confusion
    check_in_date = Column(Date, nullable=False)

    # Status options:
    # - 'completed': User did the habit
    # - 'missed': User didn't do it (auto-set by system or user)
    # - 'skipped': User intentionally skipped (doesn't count as miss for grace days)
    status = Column(String, default="completed")

    # Optional data
    minutes_logged = Column(Integer, nullable=True)  # For time tracking
    notes = Column(String, nullable=True)  # "Studied chapter 3, quiz on Friday"

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship back to habit
    habit = relationship("Habit", back_populates="check_ins")

    # IMPORTANT: Prevent duplicate check-ins for same habit on same day
    # This is a database-level constraint - the DB will reject duplicates
    __table_args__ = (
        UniqueConstraint('habit_id', 'check_in_date', name='unique_habit_date'),
    )

    def __repr__(self):
        return f"<CheckIn {self.habit_id} on {self.check_in_date}: {self.status}>"
