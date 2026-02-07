"""
Analytics Service - Calculate stats for habits and check-ins.

Provides data for the frontend charts:
- Weekly check-in counts
- Completion rates
- Streak comparisons across habits
"""

from datetime import date, timedelta
from typing import List, Dict

from sqlalchemy.orm import Session

from app.models.habit import Habit
from app.models.checkin import CheckIn
from app.models.streak import Streak


def get_weekly_checkins(db: Session, user_id: int) -> List[Dict]:
    """
    Get check-in counts for each day of the past 7 days.
    Used for the weekly bar chart.
    """
    today = date.today()
    weekly_data = []

    for i in range(6, -1, -1):  # 6 days ago to today
        day = today - timedelta(days=i)

        # Count check-ins for this day across all user's habits
        count = (
            db.query(CheckIn)
            .join(Habit)
            .filter(Habit.user_id == user_id)
            .filter(CheckIn.check_in_date == day)
            .count()
        )

        weekly_data.append({
            "date": day.isoformat(),
            "day": day.strftime("%a"),  # "Mon", "Tue", etc.
            "count": count,
        })

    return weekly_data


def get_completion_rate(db: Session, user_id: int, days: int = 30) -> float:
    """
    Calculate overall completion rate for the past N days.
    Formula: total check-ins / (active habits * days) * 100
    """
    # Count active habits
    active_habits = (
        db.query(Habit)
        .filter(Habit.user_id == user_id, Habit.is_active == True)
        .count()
    )

    if active_habits == 0:
        return 0.0

    # Count total check-ins in the period
    start_date = date.today() - timedelta(days=days)
    total_checkins = (
        db.query(CheckIn)
        .join(Habit)
        .filter(Habit.user_id == user_id)
        .filter(CheckIn.check_in_date >= start_date)
        .count()
    )

    # Calculate rate
    possible_checkins = active_habits * days
    rate = (total_checkins / possible_checkins) * 100

    return round(rate, 1)


def get_streak_comparison(db: Session, user_id: int) -> List[Dict]:
    """
    Get current streak for each habit.
    Used for the streak comparison bar chart.
    """
    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user_id, Habit.is_active == True)
        .all()
    )

    comparison = []
    for habit in habits:
        streak = db.query(Streak).filter(Streak.habit_id == habit.id).first()

        comparison.append({
            "name": habit.name,
            "current_streak": streak.current_streak if streak else 0,
            "best_streak": streak.best_streak if streak else 0,
        })

    return comparison


def get_overview(db: Session, user_id: int) -> Dict:
    """
    Get all analytics data in one call.
    The frontend calls this once to populate the entire analytics page.
    """
    return {
        "weekly_checkins": get_weekly_checkins(db, user_id),
        "completion_rate": get_completion_rate(db, user_id),
        "streak_comparison": get_streak_comparison(db, user_id),
    }
