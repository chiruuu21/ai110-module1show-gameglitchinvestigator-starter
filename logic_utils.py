"""Core game logic for the number guessing game.

Kept free of Streamlit imports so it can be unit tested on its own.
"""

DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    "Hard": (1, 50),
}

DEFAULT_RANGE = (1, 100)

# FIX: the original code paired "Too High" with "Go HIGHER!" and "Too Low" with
# "Go LOWER!", sending the player the wrong way. Reversed with agent mode and
# locked in by regression tests in tests/test_game_logic.py.
HINT_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    return DIFFICULTY_RANGES.get(difficulty, DEFAULT_RANGE)


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    # FIX: added .strip() with agent mode so " 42 " parses instead of erroring.
    raw = raw.strip()

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    # FIX: narrowed from a bare `except Exception`, but OverflowError must stay —
    # int(float("inf")) raises it, and catching only ValueError crashed the app on
    # input like "inf" or "1e400". Caught by edge-case testing during agent mode.
    except (ValueError, OverflowError):
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    Returns one of: "Win", "Too High", "Too Low"
    """
    # FIX: the original wrapped this in try/except TypeError and fell back to
    # comparing str(guess) against secret, which hid the type bug behind silently
    # wrong alphabetical results. Fallback deleted with agent mode; both values
    # are now always ints, and the return is a plain outcome string so the
    # existing tests in tests/test_game_logic.py pass unmodified.
    if guess == secret:
        return "Win"

    if guess > secret:
        return "Too High"

    return "Too Low"


def hint_message(outcome: str):
    """Return the player-facing hint text for an outcome from check_guess."""
    return HINT_MESSAGES.get(outcome, "")


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
