from friendly_traceback.syntax_errors import syntax_utils as su
from friendly_traceback import token_utils as tu


def test_highlight_token():
    tokens = tu.tokenize("\nA good test.")
    tokens = tu.remove_meaningless_tokens(tokens)
    good = tokens[1]
    assert good == "good"
    assert su.highlight_single_token(good) == {2: "  ^^^^"}


def test_highlight_two_tokens():
    tokens = tu.tokenize("abc 123 def 456 ghi")
    tokens = tu.remove_meaningless_tokens(tokens)

    first, second = tokens[1], tokens[2]
    assert first == "123"
    assert second == "def"
    assert su.highlight_two_tokens(first, second) == {1: "    ^^^ ^^^"}
    assert su.highlight_two_tokens(
        first, second, first_marker="-", second_marker="-", between="^"
    ) == {1: "    ---^---"}

    tokens = tu.tokenize("abc== def")
    tokens = tu.remove_meaningless_tokens(tokens)
    first, second = tokens[0], tokens[1]
    # No space to highlight; markers converted
    assert su.highlight_two_tokens(
        first, second, first_marker="-", second_marker=">"
    ) == {1: "^^^^^"}


def test_get_expression_before_specified_token():
    tokens = tu.tokenize("yield i = 3")  # SyntaxError
    tokens = tu.remove_meaningless_tokens(tokens)
    first = tokens[0]
    assert first == "yield"

    assert su.get_expression_before_specified_token(first, tokens, "=") == "yield i"

    # ensure that capture expression enclosed in parens
    tokens = tu.tokenize("(yield i) = 3")  # SyntaxError
    tokens = tu.remove_meaningless_tokens(tokens)
    second = tokens[1]
    assert second == "yield"
    assert su.get_expression_before_specified_token(second, tokens, "=") == "(yield i)"


def test_highlight_before_specified_token():
    tokens = tu.tokenize("yield i = 3")  # SyntaxError
    tokens = tu.remove_meaningless_tokens(tokens)
    first = tokens[0]
    assert first == "yield"

    # this highlights 'yield i'
    assert su.highlight_before_specified_token(first, tokens, "=") == {1: "^^^^^^^"}

    # ensure that capture expression enclosed in parens; highlights '(yield i)'
    tokens = tu.tokenize("(yield i) = 3")  # SyntaxError
    tokens = tu.remove_meaningless_tokens(tokens)
    second = tokens[1]
    assert second == "yield"
    assert su.highlight_before_specified_token(first, tokens, "=") == {1: "^^^^^^^^^"}
