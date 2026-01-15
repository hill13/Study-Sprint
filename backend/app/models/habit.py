"""
Habit Model
-----------
Represents a study goal or habit that users want to track.

GOAL TYPES (from your spec):
- 'daily': Simple yes/no check-in (e.g., "Study 30 minutes")
- 'frequency': Target days per week (e.g., "Study 5 days/week")
- 'time': Target hours (e.g., "Study 10 hours/week") - future extension

SCHEDULE OPTIONS:
- 'daily': Every day
- 'weekdays': Monday-Friday only
- 'custom': Specific days stored in schedule_days

STREAK RULES:
- strict_streak=True: Any miss breaks the streak
- strict_streak=False: Grace days allowed (forgiveness system)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key links this habit to a user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Basic info
    name = Column(String, nullable=False)  # e.g., "Study Math"
    description = Column(String, nullable=True)  # Optional details
    subject_tag = Column(String, nullable=True)  # e.g., "Math", "Physics"

    # Goal configuration
    goal_type = Column(String, default="daily")  # 'daily', 'frequency', 'time'
    target_frequency = Column(Integer, default=7)  # Days per week (for frequency type)
    target_minutes = Column(Integer, nullable=True)  # For time-based goals

    # Schedule
    schedule_type = Column(String, default="daily")  # 'daily', 'weekdays', 'custom'
    # For custom schedules: [0,1,2,3,4,5,6] where 0=Monday, 6=Sunday
    schedule_days = Column(JSON, default=list)

    # Streak rules - THE KEY DIFFERENTIATOR for StudySprint
    strict_streak = Column(Boolean, default=False)  # False = grace days allowed
    grace_days_per_month = Column(Integer, default=2)  # Misses allowed before streak breaks

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="habits")
    check_ins = relationship("CheckIn", back_populates="habit", cascade="all, delete-orphan")
    streak = relationship("Streak", back_populates="habit", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Habit {self.name}>"
