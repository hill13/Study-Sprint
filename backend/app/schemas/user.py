"""
User Schemas - Define the shape of user data for API requests/responses.

IMPORTANT CONCEPT: Schemas vs Models
- Models (in models/user.py): How data is STORED in database
- Schemas (this file): How data is SENT/RECEIVED via API

Why separate them?
- We NEVER want to send the password back to the user
- We might want different fields for create vs update vs response
- Validation rules might differ from storage rules
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# =============================================================================
# SCHEMA 1: UserCreate - For registration
# =============================================================================

# TODO: Create a schema for user registration
#
# Purpose:
#   Define what data is required when a new user signs up
#
# Fields needed:
#   - email: EmailStr - User's email (Pydantic validates email format automatically)
#   - username: str - Display name
#   - password: str - Plain text password (will be hashed before storing)
#
# How Pydantic works:
#   - We inherit from BaseModel
#   - Each field is defined with a type hint
#   - Pydantic automatically validates incoming data

class UserCreate(BaseModel):
    """Schema for user registration request."""
    email: EmailStr
    username: str
    password: str


# =============================================================================
# SCHEMA 2: UserLogin - For login
# =============================================================================

# TODO: Create a schema for user login
#
# Purpose:
#   Define what data is required when a user logs in
#
# Fields needed:
#   - email: EmailStr - To identify the user
#   - password: str - To verify identity
#
# Note: Username is NOT needed for login (we use email)

class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


# =============================================================================
# SCHEMA 3: UserResponse - What we send back
# =============================================================================

# TODO: Create a schema for user data in responses
#
# Purpose:
#   Define what user data we send back to the client
#   IMPORTANT: Never include password!
#
# Fields to include:
#   - id: int - User's database ID
#   - email: EmailStr - User's email
#   - username: str - Display name
#   - is_active: bool - Account status
#   - created_at: datetime - When account was created
#
# Special config needed:
#   - "from_attributes = True" tells Pydantic to read from SQLAlchemy models
#   - This lets us do: UserResponse.model_validate(db_user)

class UserResponse(BaseModel):
    """Schema for user data in API responses (never includes password)."""
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
