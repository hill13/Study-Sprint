"""
Habits Router - CRUD operations for user habits.

Endpoints:
  POST   /habits         - Create a new habit
  GET    /habits         - Get all user's habits
  GET    /habits/{id}    - Get one habit by ID
  PUT    /habits/{id}    - Update a habit
  DELETE /habits/{id}    - Delete a habit

All endpoints are protected - require valid JWT token.
Users can only access their own habits.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.habit import Habit
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from app.utils.dependencies import get_current_user


# =============================================================================
# HELPER: Convert Habit + Streak into a response-ready dict
# =============================================================================

def habit_with_streak(habit: Habit) -> dict:
    """
    Flatten streak data from the related Streak object into the habit response.

    The Habit model stores streak data in a separate 'streak' relationship,
    but the frontend expects it as top-level fields. This function pulls
    streak fields up so Pydantic can build the HabitResponse correctly.
    """
    data = {
        "id": habit.id,
        "user_id": habit.user_id,
        "name": habit.name,
        "description": habit.description,
        "subject_tag": habit.subject_tag,
        "goal_type": habit.goal_type,
        "target_frequency": habit.target_frequency,
        "target_minutes": habit.target_minutes,
        "schedule_type": habit.schedule_type,
        "schedule_days": habit.schedule_days or [],
        "strict_streak": habit.strict_streak,
        "grace_days_per_month": habit.grace_days_per_month,
        "is_active": habit.is_active,
        "created_at": habit.created_at,
    }

    # If this habit has a streak record, pull the data up to top level
    if habit.streak:
        data["current_streak"] = habit.streak.current_streak or 0
        data["best_streak"] = habit.streak.best_streak or 0
        data["streak_status"] = habit.streak.status or "safe"
        data["grace_days_used"] = habit.streak.grace_days_used or 0
        data["grace_days_reset_date"] = habit.streak.grace_days_reset_date

    return data


# =============================================================================
# ROUTER SETUP
# =============================================================================

# TODO: Create router with prefix="/habits" and tags=["Habits"]

router = APIRouter(prefix="/habits", tags=["Habits"])


# =============================================================================
# ENDPOINT 1: Create a new habit
# =============================================================================

# TODO: Create POST endpoint for creating a habit
#
# Route: POST /habits
#
# Steps:
#   1. Receive habit data from request body (HabitCreate schema)
#   2. Create new Habit object with user_id from current_user
#   3. Save to database
#   4. Return the created habit
#
# Key point: We get current_user from the token, so we know WHO is creating the habit

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new habit for the authenticated user."""
    # Step 1: Create Habit object with all fields from request + user_id
    db_habit = Habit(**habit.model_dump(), user_id=current_user.id)

    # Step 2: Save to database
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)

    # Step 3: Return the habit with streak data
    return habit_with_streak(db_habit)


# =============================================================================
# ENDPOINT 2: Get all habits for current user
# =============================================================================

# TODO: Create GET endpoint for listing all user's habits
#
# Route: GET /habits
#
# Steps:
#   1. Query database for all habits where user_id matches current user
#   2. Return list of habits

@router.get("/", response_model=List[HabitResponse])
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all habits for the authenticated user."""
    habits = (
        db.query(Habit)
        .options(joinedload(Habit.streak))  # Load streak in same query (avoids N+1)
        .filter(Habit.user_id == current_user.id)
        .all()
    )
    return [habit_with_streak(h) for h in habits]


# =============================================================================
# ENDPOINT 3: Get one habit by ID
# =============================================================================

# TODO: Create GET endpoint for fetching a single habit
#
# Route: GET /habits/{habit_id}
#
# Steps:
#   1. Query database for habit with matching id AND user_id
#   2. If not found, return 404 error
#   3. Return the habit
#
# Security: We check user_id to prevent users from accessing others' habits

@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific habit by ID."""
    # Step 1: Find habit by ID and user_id (with streak loaded)
    habit = (
        db.query(Habit)
        .options(joinedload(Habit.streak))
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    # Step 2: If not found, raise 404
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Step 3: Return the habit with streak data
    return habit_with_streak(habit)


# =============================================================================
# ENDPOINT 4: Update a habit
# =============================================================================

# TODO: Create PUT endpoint for updating a habit
#
# Route: PUT /habits/{habit_id}
#
# Steps:
#   1. Find the habit (must belong to current user)
#   2. If not found, return 404
#   3. Update only the fields that were provided (not None)
#   4. Save changes
#   5. Return updated habit

@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing habit."""
    # Step 1: Find the habit (with streak loaded)
    habit = (
        db.query(Habit)
        .options(joinedload(Habit.streak))
        .filter(Habit.id == habit_id, Habit.user_id == current_user.id)
        .first()
    )

    # Step 2: If not found, raise 404
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Step 3: Update only provided fields
    update_data = habit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)

    # Step 4: Save changes
    db.commit()
    db.refresh(habit)

    # Step 5: Return updated habit with streak data
    return habit_with_streak(habit)


# =============================================================================
# ENDPOINT 5: Delete a habit
# =============================================================================

# TODO: Create DELETE endpoint for removing a habit
#
# Route: DELETE /habits/{habit_id}
#
# Steps:
#   1. Find the habit (must belong to current user)
#   2. If not found, return 404
#   3. Delete from database
#   4. Return success message

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a habit."""
    # Step 1: Find the habit
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()

    # Step 2: If not found, raise 404
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Step 3: Delete from database
    db.delete(habit)
    db.commit()

    # Step 4: Return nothing (204 No Content)
    return None
