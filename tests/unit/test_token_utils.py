from friendly_traceback import token_utils

# Note: most of the tests involving untokenize have
# been adapted from https://github.com/myint/untokenize


def check(source):
    tokens = token_utils.tokenize(source)
    new_source = token_utils.untokenize(tokens)
    assert source == new_source


def check_lines(source):
    lines = token_utils.get_lines(source)
    tokens = []
    for line in lines:
        tokens.extend(line)
    assert source == token_utils.untokenize(tokens)


def test_untokenize():
    check(
        '''

def zap():

    """Hello zap.

  """; 1


    x \t= \t\t  \t 1


'''
    )


def test_untokenize_with_tab_indentation():
    check(
        """
if True:
\tdef zap():
\t\tx \t= \t\t  \t 1
"""
    )


def test_untokenize_with_backslash_in_comment():
    check(
        r'''
def foo():
    """Hello foo."""
    def zap(): bar(1) # \
'''
    )


def test_untokenize_with_escaped_newline():
    check(
        r'''def foo():
    """Hello foo."""
    x = \
            1
'''
    )


def test_cpython_bug_35107():
    # Checking https://bugs.python.org/issue35107#msg328884
    check("#")
    check("#\n")


def test_last_line_empty():
    """If the last line contains only space characters with no newline
    Python's tokenizer drops this content. To ensure that the
    tokenize-untokenize returns the original value, we have introduced
    a fix in our utility functions"""

    source = "a\n  "
    source_2 = "a\n\t"
    check(source)
    check(source_2)

    check_lines(source)
    check_lines(source_2)


source1 = "a = b"
source2 = "a = b # comment\n"
source3 = """
if True:
    a = b # comment
"""
tokens1 = token_utils.tokenize(source1)
tokens2 = token_utils.tokenize(source2)
lines3 = token_utils.get_lines(source3)


def test_dedent():
    new_tokens = token_utils.dedent(lines3[2], 4)
    assert new_tokens == tokens2


def test_indent():
    new_tokens = token_utils.indent(tokens2, 4)
    new_line_a = token_utils.untokenize(new_tokens)
    new_line_b = token_utils.untokenize(lines3[2])
    assert new_line_a == new_line_b


def test_self():
    with open(__file__, "r") as f:
        source = f.read()
    check(source)


def test_find_substring_index():
    assert token_utils.find_substring_index(source2, source3) == -1
    assert token_utils.find_substring_index(source3, source2) == 3


def test_immediately_before_and_after():
    tokens = token_utils.get_significant_tokens("**/ =")
    assert tokens[0].immediately_before(tokens[1])
    assert tokens[1].immediately_after(tokens[0])
    assert not tokens[1].immediately_before(tokens[2])
    assert not tokens[2].immediately_after(tokens[1])

def test_unclosed_triple_quoted_string():
    with open("tests/unclosed.txt") as f:
        source = f.read()
        assert token_utils.untokenize(token_utils.tokenize(source)) == source

def test_unterminated_string():
    # See https://github.com/friendly-traceback/friendly-traceback/issues/241
    with open("tests/unterminated.txt") as f:
        source = f.read()
        assert token_utils.untokenize(token_utils.tokenize(source)) == source


def test_strip_commment():
    statement = "if True: # a comment"
    stripped = token_utils.strip_comment(statement)
    assert stripped.strip() == "if True:"


def test_invalid_octal():
    # See https://github.com/friendly-traceback/friendly-traceback/issues/242
    check("b = 0o1876 + 0o2")
    check("a = 0o23 + 0O2987")

def test_non_printable_character():
    check('print\x17("Hello")')
