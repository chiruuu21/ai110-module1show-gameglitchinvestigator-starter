import random
import streamlit as st

# FIX: Refactored the four core logic functions into logic_utils.py using agent mode.
from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    hint_message,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    # FIX: was 1, which burned an attempt before the first guess and disagreed
    # with New Game's reset to 0. Off-by-one spotted by agent mode during review.
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# FIX: added with agent mode so New Game can clear the guess box (see key= below).
if "game_id" not in st.session_state:
    st.session_state.game_id = 0

st.subheader("Make a guess")

st.info(
    f"Guess a number between 1 and 100. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    # FIX: game_id added to the key with agent mode; a changed key makes Streamlit
    # treat this as a new widget, so the old guess doesn't linger after New Game.
    key=f"guess_input_{difficulty}_{st.session_state.game_id}",
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # FIX: New Game used to reset only attempts and secret, never status. After a
    # win/loss the rerun hit the status guard below and st.stop(), freezing the app.
    # Diagnosed with agent mode and confirmed with a Streamlit AppTest script.
    # FIX: secret now drawn from (low, high) instead of a hardcoded 1-100, which
    # ignored difficulty and could pick a secret outside the Easy/Hard range.
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.game_id += 1
    st.session_state.new_game_started = True
    st.rerun()

# FIX: st.success() used to run just before st.rerun(), which discards everything
# drawn so far, so the message was never visible. Agent mode suggested deferring it
# via a session flag; pop() reads and clears it so it shows exactly once.
if st.session_state.pop("new_game_started", False):
    st.success("New game started.")

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIX: the secret used to be cast with str() on even-numbered attempts,
        # forcing alphabetical comparison ("9" > "100"), so hints flipped on half
        # the guesses. Cast removed with agent mode; always compare int to int.
        outcome = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(hint_message(outcome))

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
