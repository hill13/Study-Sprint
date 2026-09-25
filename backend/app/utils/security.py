"""
Security utilities for password hashing.

This module handles:
- Hashing passwords when users register
- Verifying passwords when users login
- Creating JWT tokens after successful login
- Decoding JWT tokens to verify user identity
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
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


# =============================================================================
# PASSWORD RESET TOKENS
# =============================================================================
#
# A reset token is a temporary key to an account, so it is deliberately NOT an
# access token. Two properties keep it safe:
#
#   1. "type" claim - a reset token cannot be used as a login token, and a
#      stolen login token cannot be used to reset a password. Without this,
#      both are just "a JWT signed with SECRET_KEY" and become interchangeable.
#
#   2. "pwf" claim (password fingerprint) - a hash of the CURRENT password
#      hash. Resetting the password changes the stored hash, which changes the
#      fingerprint, which makes every previously issued token stop matching.
#      That gives single-use tokens with no database table to store or clean up,
#      and it silently invalidates old tokens whenever the password changes.

PASSWORD_RESET_TOKEN_TYPE = "password_reset"


def password_fingerprint(hashed_password: str) -> str:
    """
    Derive a short, stable fingerprint from a stored password hash.

    Used to tie a reset token to one specific password. We hash the hash rather
    than embedding it so the token never carries the bcrypt digest itself.
    """
    return hashlib.sha256(hashed_password.encode()).hexdigest()[:16]


def create_password_reset_token(email: str, hashed_password: str) -> str:
    """
    Create a short-lived, single-use token for resetting a password.

    Args:
        email: Identifies the account the token unlocks
        hashed_password: The user's CURRENT hash, used to build the fingerprint

    Returns:
        Encoded JWT reset token
    """
    expire = datetime.utcnow() + timedelta(
        minutes=settings.password_reset_token_expire_minutes
    )

    to_encode = {
        "sub": email,
        "exp": expire,
        "type": PASSWORD_RESET_TOKEN_TYPE,
        "pwf": password_fingerprint(hashed_password),
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_password_reset_token(token: str) -> Optional[dict]:
    """
    Decode and sanity-check a password reset token.

    Returns:
        {"email": ..., "fingerprint": ...} if the token is well-formed, signed
        by us, unexpired, and actually a reset token. None otherwise.

    Note this does NOT confirm the fingerprint still matches the stored hash -
    that needs a database lookup and happens in the route handler.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        # Covers a bad signature, a malformed token, and an expired one
        return None

    # Reject anything that is not specifically a reset token (e.g. a login token)
    if payload.get("type") != PASSWORD_RESET_TOKEN_TYPE:
        return None

    email = payload.get("sub")
    fingerprint = payload.get("pwf")
    if not email or not fingerprint:
        return None

    return {"email": email, "fingerprint": fingerprint}
