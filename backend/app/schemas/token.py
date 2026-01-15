"""
Token Schemas - Define the shape of authentication token responses.

When a user successfully logs in, we send back:
1. The JWT token itself (access_token)
2. The type of token (token_type = "bearer")
"""

from typing import Optional

from pydantic import BaseModel


# =============================================================================
# SCHEMA 1: Token - The login response
# =============================================================================

# TODO: Create a schema for the token response after login
#
# Purpose:
#   Define what we send back when user successfully logs in
#
# Fields needed:
#   - access_token: str - The JWT token string
#   - token_type: str - Always "bearer" for our API
#
# Example response:
#   {
#     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
#     "token_type": "bearer"
#   }

class Token(BaseModel):
    """Schema for token response after successful login."""
    access_token: str
    token_type: str


# =============================================================================
# SCHEMA 2: TokenData - Decoded token contents
# =============================================================================

# TODO: Create a schema for the data inside a decoded token
#
# Purpose:
#   When we decode a JWT token, we get the data back
#   This schema defines what that data looks like
#
# Fields needed:
#   - email: Optional[str] - The user's email (we stored this as "sub" in the token)
#
# Why Optional?
#   - If token is invalid or missing, email might be None
#   - We handle this gracefully instead of crashing
#
# Note: This is used internally when verifying tokens, not sent to users

class TokenData(BaseModel):
    """Schema for data extracted from a decoded JWT token."""
    email: Optional[str] = None
