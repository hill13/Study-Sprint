"""
Security utilities for password hashing.

This module handles:
- Hashing passwords when users register
- Verifying passwords when users login
"""

from passlib.context import CryptContext

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
