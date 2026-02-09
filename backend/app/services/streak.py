"""
Streak Service - Core logic for streak tracking and grace days.

This is the HEART of StudySprint - what makes it different from other habit trackers!

Status Flow:
- "safe"       → All good, grace days available
- "grace_used" → Used a grace day, but still have more
- "at_risk"    → Used ALL grace days - next miss breaks streak!
- "broken"     → Streak reset to 0

The grace day system keeps users motivated even when they miss a day.
"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.habit import Habit
from app.models.streak import Streak
from app.models.checkin import CheckIn


# =============================================================================
# FUNCTION 1: Get or create streak for a habit
# =============================================================================

# TODO: Create function to get existing streak or create new one
#
# Purpose:
#   Every habit needs a streak record. This function ensures one exists.
#
# Steps:
#   1. Try to find existing streak for this habit
#   2. If not found, create a new one with default values
#   3. Return the streak

def get_or_create_streak(db: Session, habit_id: int) -> Streak:
    """Get existing streak or create new one for a habit."""
    # Step 1: Find existing streak
    streak = db.query(Streak).filter(Streak.habit_id == habit_id).first()

    # Step 2: If not found, create new one
    if not streak:
        streak = Streak(habit_id=habit_id)
        db.add(streak)
        db.commit()
        db.refresh(streak)

    # Step 3: Return the streak
    return streak

    


# =============================================================================
# FUNCTION 2: Reset grace days if new month
# =============================================================================

# TODO: Create function to reset grace days at start of new month
#
# Purpose:
#   Grace days reset each month so users get a fresh start
#
# Steps:
#   1. Get first day of current month
#   2. If grace_days_reset_date is None or in a previous month, reset
#   3. Set grace_days_used = 0
#   4. Update grace_days_reset_date to first of current month

def reset_grace_days_if_new_month(streak: Streak, today: date):
    """Reset grace days if we're in a new month."""
    # Step 1: Get first day of current month
    first_of_month = today.replace(day=1)

    # Step 2: Check if we need to reset
    if streak.grace_days_reset_date is None or streak.grace_days_reset_date < first_of_month:
        streak.grace_days_used = 0
        streak.grace_days_reset_date = first_of_month

    


# =============================================================================
# FUNCTION 3: Update streak on check-in (CORE LOGIC)
# =============================================================================

# TODO: Create function to update streak when user checks in
#
# Purpose:
#   When a user checks in, update their streak accordingly
#
# Logic:
#   1. Get or create streak for this habit
#   2. Reset grace days if new month
#   3. If this is first check-in ever, start streak at 1
#   4. If check-in is same day, no change
#   5. If check-in is consecutive day (yesterday), increment streak
#   6. If there's a gap, handle missed days with grace logic
#   7. Update best_streak if current is higher
#   8. Update last_check_in_date and status

def update_streak_on_checkin(db: Session, habit: Habit, check_in_date: date) -> Streak:
    """Update streak when user checks in."""
    # Step 1: Get or create streak
    streak = get_or_create_streak(db, habit.id)

    # Step 2: Reset grace days if new month
    reset_grace_days_if_new_month(streak, check_in_date)

    # Step 3: Handle first check-in ever
    if streak.last_check_in_date is None:
        streak.current_streak = 1
        streak.streak_start_date = check_in_date
        streak.status = "safe"

    # Step 4: Check if same day (already checked in today)
    elif check_in_date == streak.last_check_in_date:
        pass  # No change, already checked in

    # Step 5: Check if consecutive day (yesterday)
    elif check_in_date == streak.last_check_in_date + timedelta(days=1):
         streak.current_streak += 1
         streak.status = "safe"

    # Step 6: There's a gap - calculate missed days
    else:
        missed_days = (check_in_date - streak.last_check_in_date).days - 1
        handle_missed_days(streak, habit, missed_days)
        # After handling misses, if streak not broken, increment
        if streak.status != "broken":
            streak.current_streak += 1

    # Step 7: Update best streak if current is higher
    if streak.current_streak > streak.best_streak:
         streak.best_streak = streak.current_streak

    # Step 8: Update last check-in date
    streak.last_check_in_date = check_in_date

    # Step 9: Update status based on grace days
    update_streak_status(streak, habit)

    # Step 10: Save and return
    db.commit()
    db.refresh(streak)
    return streak

    


# =============================================================================
# FUNCTION 4: Handle missed days (Grace day logic)
# =============================================================================

# TODO: Create function to handle missed days
#
# Purpose:
#   When there's a gap in check-ins, apply grace day logic
#
# Logic:
#   1. If strict_streak mode, any miss breaks the streak
#   2. Otherwise, use grace days to cover misses
#   3. If not enough grace days, break the streak

def handle_missed_days(streak: Streak, habit: Habit, missed_days: int):
    """Apply grace day logic for missed days."""
    # Step 1: Check if strict streak mode
    if habit.strict_streak:
        reset_streak(streak)
        return

    # Step 2: Calculate how many grace days available
    grace_available = habit.grace_days_per_month - streak.grace_days_used

    # Step 3: If we have enough grace days to cover misses
    if missed_days <= grace_available:
        streak.grace_days_used += missed_days
    else:
         # Not enough grace days - streak breaks
        reset_streak(streak)

    


# =============================================================================
# FUNCTION 5: Reset streak (when broken)
# =============================================================================

# TODO: Create function to reset streak to 0
#
# Steps:
#   1. Set current_streak to 0
#   2. Set status to "broken"
#   3. Clear streak_start_date
#   4. Keep best_streak (don't reset all-time record!)

def reset_streak(streak: Streak):
    """Reset streak to 0."""
    streak.current_streak = 0
    streak.status = "broken"
    streak.streak_start_date = None

    


# =============================================================================
# FUNCTION 6: Update streak status
# =============================================================================

# TODO: Create function to update status based on grace days
#
# Logic:
#   - If streak is 0: "broken"
#   - If grace_days_used == 0: "safe"
#   - If grace_days_used < max: "grace_used"
#   - If grace_days_used >= max: "at_risk"

def update_streak_status(streak: Streak, habit: Habit):
    """Update status based on grace days remaining."""
    if streak.current_streak == 0:
        streak.status = "broken"
    elif streak.grace_days_used == 0:
        streak.status = "safe"
    elif streak.grace_days_used >= habit.grace_days_per_month:
        streak.status = "at_risk"
    else:
        streak.status = "grace_used"

