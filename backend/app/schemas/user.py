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

from pydantic import BaseModel, EmailStr, Field


# Shared password rules.
#   min 8  - a floor worth enforcing on any real account
#   max 72 - bcrypt only reads the first 72 BYTES of input, so anything longer
#            is silently truncated. Rejecting it is clearer than pretending a
#            100-character password is fully checked.
PasswordStr = Field(min_length=8, max_length=72)


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
    password: str = PasswordStr


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


# =============================================================================
# SCHEMA 4: Password reset
# =============================================================================


class ForgotPasswordRequest(BaseModel):
    """Schema for requesting a password reset link."""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """
    Response for a reset request.

    The message is intentionally identical whether or not the email exists -
    a different response would let anyone probe which emails are registered.

    reset_token is only populated when settings.expose_reset_token is on
    (development convenience, since no email provider is configured).
    """
    message: str
    reset_token: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    """Schema for completing a password reset."""
    token: str
    new_password: str = PasswordStr


class MessageResponse(BaseModel):
    """Generic one-line message response."""
    message: str
