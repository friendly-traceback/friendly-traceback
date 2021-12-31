from friendly_traceback.syntax_errors import syntax_utils as su
from friendly_traceback import token_utils as tu


def test_highlight_token():
    tokens = tu.tokenize("\nA good test.")
    tokens = tu.remove_meaningless_tokens(tokens)
    good = tokens[1]
    assert good == "good"
    assert su.highlight_single_token(good) == {2: "  ^^^^"}
