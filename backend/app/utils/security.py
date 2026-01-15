"""
Security utilities for password hashing.

This module handles:
- Hashing passwords when users register
- Verifying passwords when users login
- Creating JWT tokens after successful login
- Decoding JWT tokens to verify user identity
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings

# =============================================================================
# PASSWORD HASHING SETUP
# =============================================================================

# TODO: Create a CryptContext object for bcrypt
#
# What is CryptContext?
#   - It's passlib's way of managing password hashing
#   - We tell it which algorithm to use (bcrypt)
#   - It handles all the complexity for us
#
# What we need to configure:
#   - schemes: List of hashing algorithms to use ["bcrypt"]
#   - deprecated: What to do with old hashes - set to "auto"
#
# Example of what this will look like:
#   pwd_context = CryptContext(schemes=[...], deprecated=...)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================================================
# FUNCTION 1: Hash a password
# =============================================================================

# TODO: Create function to hash a plain text password
#
# Purpose:
#   When a user registers, take their password and convert it to a hash
#
# Input:
#   - password: str - The plain text password (e.g., "MyPassword123")
#
# Output:
#   - str - The hashed password (e.g., "$2b$12$LQv3c...")
#
# Steps:
#   1. Take the plain text password
#   2. Use pwd_context.hash() to create the hash
#   3. Return the hashed string

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: The plain text password from user input

    Returns:
        The hashed password string to store in database
    """
    return pwd_context.hash(password)


# =============================================================================
# FUNCTION 2: Verify a password
# =============================================================================

# TODO: Create function to verify a password against its hash
#
# Purpose:
#   When a user logs in, check if their password matches the stored hash
#
# Input:
#   - plain_password: str - What the user typed (e.g., "MyPassword123")
#   - hashed_password: str - What's stored in database (e.g., "$2b$12$LQv3c...")
#
# Output:
#   - bool - True if password matches, False if not
#
# Steps:
#   1. Take both the plain password and hashed password
#   2. Use pwd_context.verify() to compare them
#   3. Return True or False

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: The password the user typed in login form
        hashed_password: The hash stored in the database

    Returns:
        True if password is correct, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# JWT TOKEN SETUP
# =============================================================================

# TODO: Load settings from config
#
# Why do we need settings?
#   - SECRET_KEY: The key used to sign tokens (from .env file)
#   - ALGORITHM: "HS256" - the signing method
#   - ACCESS_TOKEN_EXPIRE_MINUTES: How long token is valid (30 min default)
#
# We use get_settings() to load these values

settings = get_settings()


# =============================================================================
# FUNCTION 3: Create an access token
# =============================================================================

# TODO: Create function to generate a JWT access token
#
# Purpose:
#   After user logs in successfully, create a token they can use for future requests
#
# Input:
#   - data: dict - Information to encode in token (e.g., {"sub": "user@email.com"})
#   - expires_delta: Optional[timedelta] - Custom expiration time (optional)
#
# Output:
#   - str - The encoded JWT token string
#
# Steps:
#   1. Make a copy of the data dict (don't modify original)
#   2. Calculate expiration time:
#      - If expires_delta provided, use it
#      - Otherwise, use default from settings (30 minutes)
#   3. Add expiration time to the data with key "exp"
#   4. Encode everything using jwt.encode(data, secret_key, algorithm)
#   5. Return the token string

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing claims (e.g., {"sub": "user@email.com"})
              "sub" (subject) is the standard claim for user identifier
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    # Step 1: Copy the data so we don't modify the original
    to_encode = data.copy()

    # Step 2: Calculate when token expires
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    # Step 3: Add expiration to the token data
    to_encode["exp"] = expire

    # Step 4: Create the token using jwt.encode()
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    # Step 5: Return the token
    return encoded_jwt
