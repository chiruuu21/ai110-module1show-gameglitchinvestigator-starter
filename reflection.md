# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, a couple of things were clearly wrong. The high/low hints were backwards on some guesses, so I'd get "GO HIGHER" when I should've gotten "GO LOWER." Also, once you won a game, clicking "New Game" didn't actually restart anything — it just got stuck showing "You already won."

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

  Claude, running as Claude Code inside VS Code.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

  I told it the New Game button wasn't working, and it figured out that the code reset some variables (like attempts and the secret number) but forgot to reset status, so the app still thought I'd already won. I checked this by winning a game, clicking New Game, and seeing the old message stay — then after the fix, the game actually restarted properly.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

  When I said winning didn't show a "You won!" message, the AI pointed out a type-comparison bug and said it fixed it but it didn't. It turned out I was pressing Enter instead of clicking the Submit button, which meant my guess was never actually submitted. 

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

  I stopped trusting "it looks fixed" and started requiring actual tests before believing a bug was gone, especially since some bugs only showed up every other guess. I used the AppTest tool to script out scenarios like winning, losing, and clicking New Game, and checked that the app's state was correct every time.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.

  One test checked that guessing 9 against a secret of 100 correctly said "Too Low." The old buggy code was actually comparing numbers as text, so it said "Too High" instead (since "9" comes after "100" alphabetically). This showed me that tests only work if you pick inputs that can actually expose the bug.

- Did AI help you design or understand any tests? How?

  The AI helped write these tests, but the real value was making it run them against the old broken code to prove they actually caught something. One test I wrote passed even on the buggy version, so I deleted it. The AI also caught its own mistake when a fix it made would have crashed on inputs like inf, and fixed that too.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

  Streamlit doesn't wait around like a normal program — every time you click anything, it reruns your whole script from the top. That's why st.session_state matters: it's the only thing that survives between reruns, so the secret number and score have to live there. I also learned that st.button() only returns True for one single rerun, which is exactly why pressing Enter instead of clicking Submit made my guess disappear — the button variable was False on that rerun, so nothing happened.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

  The habit I want to keep is to never trust that a bug is fixed until I've actually tested it failing first. Twice in this project, something that sounded totally correct turned out to be wrong once I actually ran it — so now I always test my fixes against the broken version first.

- What is one thing you would do differently next time you work with AI on a coding task?

  I would describe exactly how I found a bug instead of just what I saw. Leaving out that I was pressing Enter (not clicking Submit) sent the AI down the wrong path entirely. I'd also double-check every change the AI makes instead of just accepting it. I actually rejected one of its fixes because I didn't want a second hidden way to submit a guess.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  I used to think AI code was either obviously right or obviously broken, so any mistake would be easy to spot. This project showed me that is not true. The logical bugs were the ones that ran fine and looked professional but were quietly wrong underneath. For example, the old check_guess function caught a type error instead of letting it crash, and just silently gave the wrong hint instead and nothing about the running app hinted that anything was broken. I only found out by actually testing it. That taught me that something sounding right isn't the same as it being right, so now I treat AI code as a draft to test, not a perfect logical coder.
