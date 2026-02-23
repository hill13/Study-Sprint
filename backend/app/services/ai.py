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

        # Count how many days they checked in over the last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)

        checkin_count = (
            db.query(CheckIn)
            .filter(
                CheckIn.habit_id == habit.id,
                CheckIn.check_in_date >= thirty_days_ago,
            )
            .count()
        )                                                                    # → 18

        # Get the actual check-in dates (so AI can spot day-of-week patterns)
        # We only select check_in_date, not the whole row — more efficient
        checkin_rows = (
            db.query(CheckIn.check_in_date)
            .filter(
                CheckIn.habit_id == habit.id,
                CheckIn.check_in_date >= thirty_days_ago,
            )
            .order_by(CheckIn.check_in_date)
            .all()
        )

        # Each row is a tuple like (datetime.date(2026, 1, 22),)
        # row[0] extracts just the date, .isoformat() turns it into "2026-01-22"
        date_list = [row[0].isoformat() for row in checkin_rows]            # → ["2026-01-22", "2026-01-23", ...]

        lines.append(f"  Check-ins (last 30 days): {checkin_count} out of 30")          # → "  Check-ins (last 30 days): 18 out of 30"
        lines.append(f"  Check-in dates: {', '.join(date_list) if date_list else 'none'}")  # → "  Check-in dates: 2026-01-22, 2026-01-23, ..."
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


def stream_insights(db: Session, user_id: int) -> Generator[str, None, None]:
    """
    Call Gemini and yield response text chunk by chunk.

    This is a Python generator — the caller gets text pieces one at a time
    as Gemini produces them, instead of waiting for the full response.
    """
    settings = get_settings()

    # Step 1: Check the API key exists before doing anything else
    # If it's missing, yield an error message and stop immediately
    if not settings.gemini_api_key:
        yield "Error: Gemini API key is not configured."
        return  # stops the generator — no more yields after this

    # Step 2: Get the user's habit data as a readable text summary
    user_summary = build_user_summary(db, user_id)

    # If the user has no habits yet, no point calling Gemini
    # yield a helpful message and stop
    if "no active habits" in user_summary:
        yield "You don't have any active habits yet. Add some habits and check in for a few days, then come back for insights!"
        return

    # Step 3: Build the prompt
    # Two parts: system instructions (the AI's role) + the user's actual data

    system_prompt = """You are an encouraging study coach analyzing a student's habit tracking data.
Give exactly 3 insights formatted as bullet points:
1. What they are doing great (reference specific habits and numbers)
2. What they could improve (point out patterns like skipped days or broken streaks)
3. One concrete action they can take tomorrow to improve

Rules:
- Keep each insight to 2-3 sentences
- Be encouraging but honest
- Reference actual numbers and habit names from the data
- No generic advice — everything must be grounded in their data"""

    # Combine the instructions + user data into one message
    # This is the full text we send to Gemini
    full_prompt = f"{system_prompt}\n\nHere is the student's habit data:\n\n{user_summary}"

    # Step 4: Create the Gemini client
    #
    # genai       → the Google Gemini SDK we installed (from google import genai)
    # .Client()   → opens a connection to Google's API (like logging in before you can send a message)
    # api_key=    → proves to Google we're allowed to use the API
    # settings.gemini_api_key → reads GEMINI_API_KEY from our .env file via config.py
    #                           the key never touches the frontend — it lives server-side only
    client = genai.Client(api_key=settings.gemini_api_key)

    # Step 5: Send the prompt to Gemini with streaming enabled
    #
    # client.models                  → access the AI models available on our client
    # .generate_content_stream()     → like generate_content() but returns chunks instead of one big response
    # model="gemini-2.0-flash"       → which AI model to use (flash = fast + free tier friendly)
    # contents=full_prompt           → the full text we're sending (system instructions + user data)
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )

    # Step 6: Yield each chunk as it arrives
    #
    # response is an iterator — Gemini sends pieces as it writes them, not all at once
    # each chunk contains a few words of the response
    # chunk.text  → the actual text in this chunk (some chunks are metadata with no text — skip those)
    # yield       → sends this piece immediately to whoever called stream_insights()
    #               instead of waiting for the full response, the frontend gets words in real time
    for chunk in response:
        if chunk.text:
            yield chunk.text  # → sends "You're doing" ... "great with" ... "LeetCode!" piece by piece
