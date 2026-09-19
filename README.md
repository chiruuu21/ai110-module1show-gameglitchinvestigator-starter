# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] Describe the game's purpose.

**The game.** A number guessing game built with Streamlit. The app picks a secret
number inside a range set by the difficulty (Easy 1-20, Normal 1-100, Hard 1-50)
and you get a limited number of attempts (6, 8, and 5 respectively). After each
guess the game tells you whether to go higher or lower, updates a score, and ends
when you guess correctly or run out of attempts. A "Developer Debug Info" expander
reveals the secret, the attempt count, the score, and the guess history, which is
what made the bugs below observable in the first place.

- [x] Detail which bugs you found.

| # | Bug | Symptom |
|---|-----|---------|
| 1 | Hint messages inverted | "Too High" displayed "Go HIGHER!" and "Too Low" displayed "Go LOWER!", sending the player the wrong direction every time. |
| 2 | Secret compared as text | On even-numbered attempts the secret was cast with `str()`, so the comparison was alphabetical rather than numeric. Because `"9" > "100"`, a guess of 9 against a secret of 100 was reported "Too High". This made bug 1 look intermittent. |
| 3 | New Game froze the app | New Game reset `attempts` and `secret` but never `status`. After a win or loss the rerun reached the status guard and called `st.stop()`, leaving the page stuck on "You already won." |
| 4 | New Game ignored difficulty | The new secret came from a hardcoded `random.randint(1, 100)`, so on Easy or Hard it could sit outside the stated range and be unguessable. |
| 5 | "New game started." never appeared | `st.success()` ran immediately before `st.rerun()`, and a rerun discards everything drawn so far. |
| 6 | Attempt counter off by one | A fresh page load set `attempts = 1` before any guess, so "Attempts left" was short by one and disagreed with New Game's reset to 0. |
| 7 | `pytest` could not import `logic_utils` | `ModuleNotFoundError`, because pytest only puts the test file's own directory on `sys.path`. |

- [x] Explain what fixes you applied.

1. **Corrected the hint text.** "Too High" now maps to "Go LOWER!" and "Too Low" to
   "Go HIGHER!", via a `HINT_MESSAGES` lookup in `logic_utils.py`.
2. **Removed the `str()` cast** so the guess and the secret are always compared as
   integers. The old `try/except TypeError` fallback in `check_guess` existed only to
   mask this and was deleted — it converted a type error into a silently wrong answer.
3. **Made New Game a full reset:** `status`, `score`, and `history` are cleared
   alongside `attempts` and `secret`, so the app recovers from both a win and a loss.
4. **Drew the new secret from `(low, high)`** so it respects the chosen difficulty.
5. **Deferred the confirmation message** behind a session flag read with
   `st.session_state.pop(...)` after the rerun, so it displays exactly once.
6. **Initialised `attempts` to 0**, matching what New Game sets.
7. **Added `tests/conftest.py`** to put the project root on `sys.path`, so `pytest`
   works from any directory.
8. **Refactored the core logic into `logic_utils.py`** (`get_range_for_difficulty`,
   `parse_guess`, `check_guess`, `hint_message`, `update_score`). The module imports
   no Streamlit, so it is unit-testable on its own. `check_guess` returns the outcome
   string and `hint_message` returns the display text, which keeps the provided tests
   passing unmodified. While refactoring, `parse_guess` also gained a `.strip()` so
   `" 42 "` parses, and its exception clause catches `OverflowError` as well as
   `ValueError` — `int(float("inf"))` raises the former, which would otherwise crash
   the app on input like `inf` or `1e400`.

**Known issue not fixed:** `update_score` awards **+5** for a "Too High" guess made on
an even-numbered attempt, where every other wrong guess costs −5. This is visible at
step 3 of the walkthrough below, where a wrong guess raises the score from −5 to 0.
It was left as-is so the refactor stayed behaviour-preserving.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

The transcript below is a real game, captured by driving the app with
`streamlit.testing.v1.AppTest`. The secret was pinned to **63** so the run is
reproducible; normally it is random.

**Setup:** difficulty `Normal`, range 1-100, 8 attempts allowed, secret `63`.

1. **Open the app** with `python -m streamlit run app.py`. The banner reads
   "Attempts left: 8" and the score starts at 0. Expanding "Developer Debug Info"
   shows `Secret: 63`, `Attempts: 0`, `Score: 0`, `History: []`.
2. **Guess `40`** and click "Submit Guess 🚀". 40 is below the secret, so the game
   shows **"📈 Go HIGHER!"** — pointing the player in the correct direction, which is
   the bug that used to be reversed. Attempts becomes 1, score −5.
3. **Guess `70`.** 70 is above the secret, so the game shows **"📉 Go LOWER!"**.
   Attempts becomes 2. Note the score moves from −5 to **0** here rather than −10:
   this is the known `update_score` quirk described above, not a hint error.
4. **Guess `abc`.** The game rejects it with **"That is not a number."** and shows no
   direction hint. The attempt is still counted (attempts becomes 3) and the raw text
   is recorded in the history.
5. **Guess `60`.** Still below the secret, so **"📈 Go HIGHER!"** again. Attempts
   becomes 4, score −5. Together with step 3 this confirms the direction is now
   consistent on both odd and even attempts — the old code flipped on every second
   guess because it compared the secret as text.
6. **Guess `63`.** The game shows **"🎉 Correct!"**, releases balloons, and displays
   **"You won! The secret was 63. Final score: 35"**. Attempts is 5 and the status
   becomes `won`. The debug panel shows `History: [40, 70, 'abc', 60, 63]`.
7. **Click "New Game 🔁".** The app restarts cleanly instead of freezing: status
   returns to `playing`, attempts and score return to 0, the history empties, the
   guess box is cleared, a new secret is drawn from the current difficulty's range,
   and **"New game started."** is displayed. Before the fix this step left the page
   permanently stuck on "You already won. Start a new game to play again."
8. **Losing works too.** On Hard (5 attempts), five wrong guesses end the game with
   **"Out of attempts! The secret was …"**, and New Game recovers from that state as
   well.

**Note on submitting:** guesses are submitted by clicking "Submit Guess 🚀". Pressing
Enter in the text box does not submit — Streamlit only reports a button as pressed on
the rerun where it is actually clicked.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ pytest tests/
============================= test session starts ==============================
platform darwin -- Python 3.12.2, pytest-7.4.4, pluggy-1.0.0
rootdir: /Users/chiragdhungana/ai110Project1
plugins: anyio-4.6.2
collected 7 items

tests/test_game_logic.py .......                                         [100%]

============================== 7 passed in 0.02s ===============================
```

The 7 tests are the 3 provided with the assignment plus 4 regression tests added
for the bugs fixed above:

| Test | What it guards |
|------|----------------|
| `test_winning_guess` | A matching guess returns `"Win"`. |
| `test_guess_too_high` | A guess above the secret returns `"Too High"`. |
| `test_guess_too_low` | A guess below the secret returns `"Too Low"`. |
| `test_too_high_hint_tells_player_to_go_lower` | "Too High" shows "Go LOWER!", not "Go HIGHER!". |
| `test_too_low_hint_tells_player_to_go_higher` | "Too Low" shows "Go HIGHER!", not "Go LOWER!". |
| `test_hints_for_opposite_outcomes_are_different` | The two directions never collapse to the same message. |
| `test_guess_compared_as_number_not_as_text` | `check_guess(9, 100)` is "Too Low" — numeric comparison, not alphabetical. |

The four regression tests were validated by running them against a reconstruction
of the original buggy logic: three of them failed on it and pass on the fixed code,
which is what makes them meaningful rather than decorative.

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
