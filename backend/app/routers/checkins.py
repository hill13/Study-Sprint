"""
CheckIns Router - Record daily habit completions.

Endpoints:
  POST   /checkins              - Record a check-in (updates streak!)
  GET    /checkins              - Get check-ins for a habit
  DELETE /checkins/{id}         - Delete a check-in

The POST endpoint is the CORE of StudySprint - it triggers streak calculations!
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.checkin import CheckIn
from app.models.habit import Habit
from app.models.user import User
from app.schemas.checkin import CheckInCreate, CheckInResponse
from app.utils.dependencies import get_current_user
from app.services.streak import update_streak_on_checkin


# =============================================================================
# ROUTER SETUP
# =============================================================================

# TODO: Create router with prefix="/checkins" and tags=["Check-ins"]

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


# =============================================================================
# ENDPOINT 1: Create a check-in (THE MAIN ONE!)
# =============================================================================

# TODO: Create POST endpoint for recording a check-in
#
# Route: POST /checkins
#
# Steps:
#   1. Verify the habit belongs to current user
#   2. Set check_in_date to today if not provided
#   3. Check if check-in already exists for this habit+date
#   4. Create the check-in record
#   5. Call update_streak_on_checkin() to update streak!
#   6. Return the check-in

@router.post("/", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_checkin(
    checkin: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a check-in for a habit. This updates the streak!"""
    # Step 1: Verify habit belongs to current user
    habit = db.query(Habit).filter(Habit.id == checkin.habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Step 2: Set check_in_date to today if not provided
    check_in_date = checkin.check_in_date or date.today()

    # Step 3: Check if already checked in for this date
    existing = db.query(CheckIn).filter(
        CheckIn.habit_id == checkin.habit_id,
        CheckIn.check_in_date == check_in_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in for this date")

    # Step 4: Create the check-in
    db_checkin = CheckIn(
        habit_id=checkin.habit_id,
        check_in_date=check_in_date,
        status=checkin.status,
        minutes_logged=checkin.minutes_logged,
        notes=checkin.notes
    )
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)

    # Step 5: Update the streak!
    update_streak_on_checkin(db, habit, check_in_date)

    # Step 6: Return the check-in
    return db_checkin

    


# =============================================================================
# ENDPOINT 2: Get check-ins for a habit
# =============================================================================

# TODO: Create GET endpoint for listing check-ins
#
# Route: GET /checkins?habit_id=1
#
# Steps:
#   1. Verify the habit belongs to current user
#   2. Query check-ins for this habit
#   3. Return list of check-ins

@router.get("/", response_model=List[CheckInResponse])
def get_checkins(
    habit_id: int = Query(..., description="The habit to get check-ins for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all check-ins for a specific habit."""
    # Step 1: Verify habit belongs to current user
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Step 2: Query check-ins for this habit
    checkins = db.query(CheckIn).filter(CheckIn.habit_id == habit_id).order_by(CheckIn.check_in_date.desc()).all()

    # Step 3: Return check-ins
    return checkins

    


# =============================================================================
# ENDPOINT 3: Delete a check-in
# =============================================================================

# TODO: Create DELETE endpoint for removing a check-in
#
# Route: DELETE /checkins/{checkin_id}
#
# Steps:
#   1. Find the check-in
#   2. Verify the habit belongs to current user
#   3. Delete the check-in
#   4. Return success

@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkin(
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a check-in."""
    # Step 1: Find the check-in
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")

    # Step 2: Verify habit belongs to current user
    habit = db.query(Habit).filter(Habit.id == checkin.habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Check-in not found")

    # Step 3: Delete the check-in
    db.delete(checkin)
    db.commit()

    # Step 4: Return nothing (204 No Content)
    return None

    
