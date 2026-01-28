"""
Authentication Dependencies - Protect endpoints with JWT token verification.

This module provides:
- get_current_user: Extract and verify JWT token, return the logged-in user

Usage in endpoints:
    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        # Only authenticated users reach here
        return {"message": f"Hello {current_user.username}"}
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.token import TokenData


# =============================================================================
# OAUTH2 SCHEME SETUP
# =============================================================================

# TODO: Create OAuth2PasswordBearer instance
#
# What is OAuth2PasswordBearer?
#   - A helper that extracts token from "Authorization: Bearer <token>" header
#   - tokenUrl="/auth/login" → Points to our login endpoint (for Swagger UI)
#
# Example:
#   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Load settings for JWT verification
settings = get_settings()


# =============================================================================
# FUNCTION: Get current user from token
# =============================================================================

# TODO: Create function to verify token and return current user
#
# Steps:
#   1. Define credentials_exception (reused for any auth failure)
#   2. Try to decode the JWT token using jwt.decode()
#   3. Extract email from token payload (it's in "sub" field)
#   4. If no email, raise exception
#   5. Look up user in database by email
#   6. If user not found, raise exception
#   7. Return the user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Verify JWT token and return the current user.

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    # Step 1: Create exception to reuse for any auth failure
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Steps 2-4: Decode token and extract email
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # Step 5: Find user in database
    user = db.query(User).filter(User.email == token_data.email).first()

    # Step 6: If not found, raise exception
    if user is None:
        raise credentials_exception

    # Step 7: Return the user
    return user
