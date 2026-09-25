"""
Authentication Router - Handles user registration and login.

Endpoints:
  POST /auth/register        - Create a new user account
  POST /auth/login           - Authenticate and get access token
  POST /auth/forgot-password - Request a password reset token
  POST /auth/reset-password  - Complete a password reset
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    MessageResponse,
)
from app.schemas.token import Token
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_password_reset_token,
    verify_password_reset_token,
    password_fingerprint,
)

logger = logging.getLogger(__name__)
settings = get_settings()


# =============================================================================
# ROUTER SETUP
# =============================================================================

# TODO: Create an APIRouter instance
#
# What is APIRouter?
#   - Groups related endpoints together
#   - prefix="/auth" means all routes start with /auth
#   - tags=["Authentication"] groups them in API docs
#
# Example:
#   router = APIRouter(prefix="/auth", tags=["Authentication"])

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# ENDPOINT 1: Register a new user
# =============================================================================

# TODO: Create POST endpoint for user registration
#
# Route: POST /auth/register
#
# What this endpoint does:
#   1. Receive user data (email, username, password)
#   2. Check if email already exists → if yes, return error
#   3. Check if username already exists → if yes, return error
#   4. Hash the password
#   5. Create new User in database
#   6. Return the user info (without password)
#
# Decorator explained:
#   @router.post("/register", response_model=UserResponse)
#   - "/register" → full path becomes /auth/register
#   - response_model=UserResponse → FastAPI auto-formats response
#
# Function parameters:
#   - user: UserCreate → Pydantic validates the request body
#   - db: Session = Depends(get_db) → Database connection (dependency injection)
#
# HTTPException:
#   - Used to return error responses with proper status codes
#   - status_code=400 → Bad request (user error)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - Validates email and username are unique
    - Hashes password before storing
    - Returns created user (without password)
    """
    # Step 1: Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Step 2: Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Step 3: Hash the password
    hashed = hash_password(user.password)

    # Step 4: Create new User object
    db_user = User(email=user.email, username=user.username, hashed_password=hashed)

    # Step 5: Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Step 6: Return the user
    return db_user


# =============================================================================
# ENDPOINT 2: Login user
# =============================================================================

# TODO: Create POST endpoint for user login
#
# Route: POST /auth/login
#
# What this endpoint does:
#   1. Receive credentials (email, password)
#   2. Find user by email → if not found, return error
#   3. Verify password → if wrong, return error
#   4. Create JWT access token
#   5. Return the token
#
# Security note:
#   - Use same error message for "user not found" and "wrong password"
#   - This prevents attackers from knowing which emails exist

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    - Verifies email exists and password matches
    - Returns JWT token for authenticated requests
    """
    # Step 1: Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()

    # Step 2: Verify user exists and password is correct
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Step 3: Create access token
    access_token = create_access_token(data={"sub": user.email})

    # Step 4: Return the token
    return Token(access_token=access_token, token_type="bearer")


# =============================================================================
# ENDPOINT 3: OAuth2 Token (for Swagger UI)
# =============================================================================

# This endpoint follows OAuth2 spec for Swagger's Authorize button
# It accepts form data with "username" and "password" fields

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token endpoint for Swagger UI.

    Use this with Swagger's Authorize button.
    Enter your EMAIL in the username field.
    """
    # OAuth2 uses "username" but we use email
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


# =============================================================================
# ENDPOINT 4: Request a password reset
# =============================================================================

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Start a password reset.

    Always returns the same message, whether or not the email is registered.
    Saying "no account with that email" here would turn this endpoint into a
    way to enumerate which emails have accounts - the same reason /login uses
    one error for both a bad email and a bad password.
    """
    user = db.query(User).filter(User.email == payload.email).first()

    message = "If an account exists for that email, a reset link has been sent."

    # Unknown email: stop here, but return the identical response
    if not user:
        return ForgotPasswordResponse(message=message)

    # Bind the token to the current password hash so it can only be used once
    token = create_password_reset_token(user.email, user.hashed_password)

    # No email provider is configured, so the token goes to the server log.
    # In a real deployment this is where you would send the reset email.
    logger.info("Password reset token issued for %s: %s", user.email, token)

    if settings.expose_reset_token:
        return ForgotPasswordResponse(message=message, reset_token=token)

    return ForgotPasswordResponse(message=message)


# =============================================================================
# ENDPOINT 5: Complete a password reset
# =============================================================================

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Finish a password reset using a token from /auth/forgot-password.

    Every failure returns the same 400 so the response can't be used to tell
    an expired token from a forged one from an already-used one.
    """
    invalid_token = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token",
    )

    # Step 1: Signature, expiry, and token type
    token_data = verify_password_reset_token(payload.token)
    if token_data is None:
        raise invalid_token

    # Step 2: The account must still exist
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if user is None:
        raise invalid_token

    # Step 3: The fingerprint must still match the stored hash.
    # If the password has changed since this token was issued - including by an
    # earlier use of this very token - the fingerprints differ and it is dead.
    if password_fingerprint(user.hashed_password) != token_data["fingerprint"]:
        raise invalid_token

    # Step 4: Store the new hash. This also invalidates any other outstanding
    # reset tokens for this account, since they all carry the old fingerprint.
    user.hashed_password = hash_password(payload.new_password)
    db.commit()

    logger.info("Password reset completed for %s", user.email)

    return MessageResponse(message="Password updated. You can now log in.")
