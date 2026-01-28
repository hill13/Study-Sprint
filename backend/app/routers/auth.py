"""
Authentication Router - Handles user registration and login.

Endpoints:
  POST /auth/register - Create a new user account
  POST /auth/login    - Authenticate and get access token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.utils.security import hash_password, verify_password, create_access_token


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
