from logic_utils import check_guess, hint_message

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# --- Regression tests for the fixed bugs ---
# FIX: written with agent mode, then validated by running them against a
# reconstruction of the original buggy code to confirm all three actually fail
# on it. A regression test that passes on the broken version proves nothing.

def test_too_high_hint_tells_player_to_go_lower():
    # BUG: "Too High" used to show "Go HIGHER!", sending the player the wrong way.
    # A guess above the secret must tell the player to go LOWER.
    assert "LOWER" in hint_message("Too High")
    assert "HIGHER" not in hint_message("Too High")


def test_too_low_hint_tells_player_to_go_higher():
    # BUG: "Too Low" used to show "Go LOWER!". A guess below the secret
    # must tell the player to go HIGHER.
    assert "HIGHER" in hint_message("Too Low")
    assert "LOWER" not in hint_message("Too Low")


def test_hints_for_opposite_outcomes_are_different():
    # Guards against both outcomes accidentally mapping to the same message.
    assert hint_message("Too High") != hint_message("Too Low")


def test_guess_compared_as_number_not_as_text():
    # BUG: the secret was cast to str() on even attempts, so the comparison
    # became alphabetical. As text "9" > "100", which made a guess of 9
    # against a secret of 100 report "Too High". Fewer digits must not
    # be mistaken for a smaller number, and vice versa.
    assert check_guess(9, 100) == "Too Low"
    assert check_guess(100, 9) == "Too High"
