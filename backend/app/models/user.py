"""
User Model
----------
Stores user account information.

SECURITY NOTES:
- Never store plain text passwords
- hashed_password stores the bcrypt hash
- Email should be unique (prevents duplicate accounts)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key - unique identifier for each user
    id = Column(Integer, primary_key=True, index=True)

    # Account credentials
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Profile info
    username = Column(String, unique=True, index=True, nullable=False)

    # Account status
    is_active = Column(Boolean, default=True)

    # Timestamps - automatically set on creation/update
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship: A user has many habits
    # back_populates creates a two-way link (user.habits and habit.owner)
    habits = relationship("Habit", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
