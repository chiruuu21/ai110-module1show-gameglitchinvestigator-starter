# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|   15  |  GO HIGHER          GO LOWER          Wrong logical output
| NEW GAME| Game restart    |    Stuck        | You already won. Start a new game to play again.
|    20   | GO HIGHER         Go LOWER!         Wrong logical output

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

  Claude, running as Claude Code in agent mode inside VS Code.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

  I told the AI that the "New Game" button got stuck instead of restarting, and it correctly traced the problem to session state rather than to the button itself. Its explanation was that `new_game` reset `attempts` and `secret` but never reset `status`, so after a win `st.rerun()` restarted the script, execution reached the `if st.session_state.status != "playing"` guard a few lines below, and `st.stop()` froze the page on "You already won." I verified this two ways. In the browser I won a game, clicked New Game, and watched the old banner stay put; then we wrote a Streamlit `AppTest` script that wins a game, clicks New Game, and prints the session state. Before the fix it reported `status: won`, and after also resetting `status`, `score`, and `history` it reported `status: playing | attempts: 0 | score: 0` with no exception — and the same script confirmed the loss path on Hard difficulty recovered too.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

  When I reported that guessing the correct number didn't show that I had won, the AI told me it had already fixed that bug by deleting a `str()` cast on the secret, explaining that `guess == secret` had been comparing an `int` to a `str` and so could never be true. The explanation was detailed and sounded right, but it was wrong. We tested it by pulling the original committed file out of git (`git show HEAD:app.py`) and running it through the same `AppTest` harness, and the untouched buggy version *did* print "You won!" on both odd and even attempts — because the old `check_guess` had a `try/except TypeError` fallback that compared `str(guess) == secret` and caught the win anyway. The actual cause was that I was pressing Enter instead of clicking "Submit Guess": `st.button` only returns `True` on the exact rerun where it is clicked, so pressing Enter reran the script with `submit = False` and silently discarded my guess, leaving `attempts` at 0 with no message. The lesson I took from this is that a confident, well-written explanation is not evidence, and that the way to check one is to make the AI run the old code instead of just describing it.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

  I stopped accepting "it looks right now" as proof, because two of these bugs only appeared on every second guess and could easily look fixed by luck. For the logic bugs I required a failing-then-passing test, and for the state bugs I required a scripted run of the app rather than clicking around. I used `streamlit.testing.v1.AppTest`, which runs the app headlessly and lets a script set the text box, click buttons, and read `st.session_state` afterwards, so the same scenario could be replayed exactly. The scenarios I checked were: win on attempt 1, win on attempt 2 (the case that used to break), New Game after a win, New Game after a loss on Hard, and typing a guess without clicking Submit. All of them reported the expected `status`, `attempts`, and `score` with no exceptions, and I re-ran the whole set again after refactoring into `logic_utils.py` to confirm the move changed no behavior.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.

  The most useful test was `test_guess_compared_as_number_not_as_text`, which asserts `check_guess(9, 100) == "Too Low"` and `check_guess(100, 9) == "Too High"`. The specific numbers matter: the old code compared the guess against the secret as text on even attempts, and alphabetically `"9" > "100"`, so a guess of 9 against a secret of 100 was reported as "Too High." If I had tested with same-length numbers like 40 and 50 the test would have passed even while the bug was present, which showed me that a test only proves something if the inputs can actually distinguish the broken behavior from the correct one. I also validated the new tests by reconstructing the original buggy logic in a scratch file and running the same test file against it: three of the four new tests failed on the broken version and passed on the fixed one, which is what makes them real regression tests. One test I had written passed on the broken code too, so I deleted it rather than keep a test that proved nothing.

- Did AI help you design or understand any tests? How?

  Yes — the AI generated the regression tests, but the part that actually mattered was making it prove they worked by running them against the old buggy code, which is how we caught the one worthless test. It also found an edge case I would not have thought of: when it narrowed a broad `except Exception` in `parse_guess` down to `except ValueError`, that change would have crashed the app on input like `inf` or `1e400`, because `int(float("inf"))` raises `OverflowError` instead. It caught its own mistake by testing 13 odd inputs through `parse_guess` and fixed it to `except (ValueError, OverflowError)`. Separately, when `pytest` failed with `ModuleNotFoundError: No module named 'logic_utils'`, the AI's first guess — run it from the project root — turned out to be wrong when we tested it, and the real difference is that `python -m pytest` puts the current directory on `sys.path` while the bare `pytest` command does not; we fixed it for good with a `tests/conftest.py`.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
