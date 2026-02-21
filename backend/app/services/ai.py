"""
AI Insights Service - Generate personalized habit analysis using Google Gemini.

How it works:
1. Pull the user's habits, streaks, and check-ins from the database
2. Format that data into a prompt the AI can understand
3. Call Gemini's API with streaming enabled
4. Yield each text chunk as it arrives (for real-time display on the frontend)
"""

from datetime import date, timedelta
from typing import Generator

from google import genai
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.habit import Habit
from app.models.checkin import CheckIn
from app.models.streak import Streak


def build_user_summary(db: Session, user_id: int) -> str:
    """
    Pull habit data from the database and format it as readable text.

    Why text and not JSON? LLMs understand natural language better than
    raw data structures. We're translating database rows into sentences.
    """
    # Step a: Query all active habits for this user
    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user_id, Habit.is_active == True)
        .all()
    )

    # Edge case: user has no habits yet
    if not habits:
        return "This user has no active habits yet."

    # Start building the text summary line by line
    lines = []
    lines.append(f"Today's date: {date.today().isoformat()}")  # → "Today's date: 2026-02-20"
    lines.append(f"Number of active habits: {len(habits)}")    # → "Number of active habits: 3"
    lines.append("")                                            # → "" (blank line for readability)

    # Step b: For each habit, get its streak data
    for habit in habits:
        streak = db.query(Streak).filter(Streak.habit_id == habit.id).first()
        current_streak = streak.current_streak if streak else 0
        best_streak = streak.best_streak if streak else 0

        lines.append(f"Habit: {habit.name}")                          # → "Habit: LeetCode"
        if habit.description:
            lines.append(f"  Description: {habit.description}")       # → "  Description: Daily problem solving"
        lines.append(f"  Current streak: {current_streak} days")      # → "  Current streak: 12 days"
        lines.append(f"  Best streak: {best_streak} days")            # → "  Best streak: 20 days"

        # Step 3 (check-in dates) will be added next
        lines.append("")  # blank line between habits

    # Step d: Join all lines into one string the AI can read
    #
    # Final output looks like:
    #
    #   Today's date: 2026-02-20
    #   Number of active habits: 2
    #
    #   Habit: LeetCode
    #     Description: Daily problem solving
    #     Current streak: 12 days
    #     Best streak: 20 days
    #
    #   Habit: Reading
    #     Current streak: 5 days
    #     Best streak: 14 days
    #
    return "\n".join(lines)


# =============================================================================
# STEP 4: Stream AI insights from Gemini
# =============================================================================
#
# TODO: Create function stream_insights(db, user_id) -> Generator
#
# This function:
#   a. Define the system prompt (instructions for the AI)
#   b. Call build_user_summary() to get the user's data
#   c. Create a Gemini client using the API key from settings
#   d. Send the prompt + data to Gemini with streaming enabled
#   e. Yield each text chunk as it arrives
#
# The system prompt should tell the AI:
#   - You are a study coach
#   - Give 3 insights: what's great, what to improve, how to improve
#   - Be specific, reference actual numbers
#   - Keep each insight to 2-3 sentences
