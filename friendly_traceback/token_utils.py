"""token_utils.py
------------------

A collection of useful functions and methods to deal with tokenizing
source code.
"""

import ast
import keyword
import sys
import tokenize as py_tokenize
from io import StringIO
from typing import Any, Iterable, List, Sequence, Tuple, Union

from . import debug_helper

_TokenInfo = Union[
    py_tokenize.TokenInfo, Tuple[int, str, Tuple[int, int], Tuple[int, int], str]
]

_token_format = "type={type}  string={string}  start={start}  end={end}  line={line}"

UNCLOSED = -9
assert UNCLOSED not in py_tokenize.tok_name
py_tokenize.tok_name[UNCLOSED] = "UNCLOSED_STRING"


class Token:
    """Token as generated from Python's tokenize.generate_tokens written here in
    a more convenient form, and with some custom methods.

    The various parameters are::

        type: token type
        string: the token written as a string
        start = (start_row, start_col)
        end = (end_row, end_col)
        line: entire line of code where the token is found.

    Token instances are mutable objects. Therefore, given a list of tokens,
    we can change the value of any token's attribute, untokenize the list and
    automatically obtain a transformed source. Almost always, the attribute
    to be transformed will be the string attribute.
    """

    def __init__(self, token: _TokenInfo) -> None:
        self.type = token[0]
        self.string = token[1]
        self.start = self.start_row, self.start_col = token[2]
        self.end = self.end_row, self.end_col = token[3]
        self.line = token[4]

    def copy(self) -> "Token":
        """Makes a copy of a given token"""
        return Token((self.type, self.string, self.start, self.end, self.line))

    def __eq__(self, other: object) -> bool:
        """Compares a Token with another object; returns true if
        self.string == other.string or if self.string == other.
        """
        return self.string == str(other)

    def __repr__(self) -> str:  # pragma: no cover
        """Nicely formatted token to help with debugging session.

        Note that it does **not** print a string representation that could be
        used to create a new ``Token`` instance, which is something you should
        never need to do other than indirectly by using the functions
        provided in this module.
        """
        return _token_format.format(
            type="%s (%s)" % (self.type, py_tokenize.tok_name[self.type]),
            string=repr(self.string),
            start=str(self.start),
            end=str(self.end),
            line=repr(self.line),
        )

    def __str__(self) -> str:
        """Returns the string attribute."""
        return self.string

    def is_comment(self) -> bool:
        """Returns True if the token is a comment."""
        return self.type == py_tokenize.COMMENT

    def is_identifier(self) -> bool:
        """Returns ``True`` if the token represents a valid Python identifier
        excluding Python keywords.

        Note: this is different from Python's string method ``isidentifier``
        which also returns ``True`` if the string is a keyword.
        """
        return self.string.isidentifier() and not self.is_keyword()

    def is_name(self) -> bool:
        """Returns ``True`` if the token is a type NAME"""
        return self.type == py_tokenize.NAME

    def is_keyword(self) -> bool:
        """Returns True if the token represents a Python keyword."""
        return keyword.iskeyword(self.string) or self.string in ["__debug__", "..."]

    def is_number(self) -> bool:
        """Returns True if the token represents a number of any type"""
        return self.type == py_tokenize.NUMBER

    def is_operator(self) -> bool:
        """Returns true if the token is of type OP"""
        return self.type == py_tokenize.OP

    def is_float(self) -> bool:
        """Returns True if the token represents a float"""
        return self.is_number() and isinstance(ast.literal_eval(self.string), float)

    def is_integer(self) -> bool:
        """Returns True if the token represents an integer"""
        return self.is_number() and isinstance(ast.literal_eval(self.string), int)

    def is_complex(self) -> bool:
        """Returns True if the token represents a complex number"""
        return self.is_number() and isinstance(ast.literal_eval(self.string), complex)

    def is_space(self) -> bool:
        """Returns True if the token indicates a change in indentation,
        the end of a line, or the end of the source
        (``INDENT``, ``DEDENT``, ``NEWLINE``, ``NL``, and ``ENDMARKER``).

        Note that spaces, including tab characters ``\\t``, between tokens
        on a given line are not considered to be tokens themselves.
        """
        return self.type in (
            py_tokenize.INDENT,
            py_tokenize.DEDENT,
            py_tokenize.NEWLINE,
            py_tokenize.NL,
            py_tokenize.ENDMARKER,
        )

    def is_string(self) -> bool:
        """Returns True if the token is a string"""
        return self.type == py_tokenize.STRING

    def is_f_string(self) -> bool:
        """Return True if the token is an f-string"""
        return self.type == py_tokenize.STRING and (
            self.string.startswith("f") or self.string.startswith("F")
        )

    def is_unclosed_string(self) -> bool:
        """Returns True if the token is part of an unclosed triple-quoted string"""
        return self.type == UNCLOSED

    def immediately_before(self, other: Any) -> bool:
        """Returns True if the current token is immediately before other,
        without any intervening space in between the two tokens.
        """
        if not isinstance(other, Token):  # pragma: no cover
            return False
        return self.end_row == other.start_row and self.end_col == other.start_col

    def immediately_after(self, other: Any) -> bool:
        """Returns True if the current token is immediately after other,
        without any intervening space in between the two tokens.
        """
        if not isinstance(other, Token):  # pragma: no cover
            return False
        return other.immediately_before(self)

    def is_error(self) -> bool:
        """Returns True if the current token is an error token"""
        return self.type == py_tokenize.ERRORTOKEN

    def name(self) -> str:
        """Returns the name of the character type"""
        return py_tokenize.tok_name[self.type]


def is_assignment(op: Union[str, Token]) -> bool:
    """Returns True if op (string or Token) is an assigment or augmented assignment."""
    ops = [
        "=",
        "+=",
        "-=",
        "*=",
        "@=",
        "/=",
        "//=",
        "%=",
        "**=",
        ">>=",
        "<<=",
        "&=",
        "^=",
        "|=",
    ]
    if sys.version_info >= (3, 8):
        ops.append(":=")
    return str(op) in ops


def is_bitwise(op: Union[str, Token]) -> bool:
    """Returns True if op (string or Token) is a bitwise operator."""
    ops = ["^", "&", "|", "<<", ">>", "~"]
    return str(op) in ops


def is_comparison(op: Union[str, Token]) -> bool:
    """Returns True if op (string or Token) is a comparison operator."""
    ops = ["<", ">", "<=", ">=", "==", "!="]
    return str(op) in ops


def is_math_op(op: Union[str, Token]) -> bool:
    """Returns True if op (string or Token) is an operator that can be used
    as a binary operator in a mathematical operation.
    """
    ops = ["+", "-", "*", "**", "@", "/", "//", "%"]
    return str(op) in ops


def is_operator(op: Union[str, Token]) -> bool:
    """Returns True if op (string or token) is or could be part of one
    of the following: assigment operator, mathematical operator,
    bitwise operator, comparison operator."""
    part_ops = ["!", ":"]
    return (
        is_assignment(op)
        or is_bitwise(op)
        or is_comparison(op)
        or is_math_op(op)
        or str(op) in part_ops
    )


def fix_empty_last_line(source: str, tokens: Sequence[Token]) -> None:
    """Python's tokenizer drops entirely a last line if it consists only of
    space characters and/or tab characters.  To ensure that we can always have::

        untokenize(tokenize(source)) == source

    we correct the last token content by modifying ``tokens`` in place.
    """
    if not tokens:
        return
    nb = 0
    for char in reversed(source):
        if char in (" ", "\t"):
            nb += 1
        else:
            break
    last_token = tokens.pop()

    row = last_token.start_row
    # When dealing with an empty line, Python 3.12 generate an NL token on the last line
    # and adds a ENDMARKER token on the next (non-existent) line.
    # For previous version no NL token was inserted.
    if (
        sys.version_info >= (3, 12)
        and len(tokens) > 1
        and tokens[-1].type == py_tokenize.NL
    ):
        prev_token = tokens.pop()
        if last_token.start_row != prev_token.start_row:
            row = prev_token.start_row

    last_token.string = source[-nb:]
    last_token.start = (row, last_token.start_col)
    last_token.end = (row, last_token.end_col + len(last_token.string))
    last_token.line = last_token.string

    tokens.append(last_token)


def tokenize(source: str) -> List[Token]:
    """Transforms a source (string) into a list of Tokens.

    If an exception is raised by Python's tokenize module, the list of tokens
    accumulated up to that point is returned.
    """
    tokens = []
    try:
        for tok in py_tokenize.generate_tokens(StringIO(source).readline):
            token = Token(tok)
            tokens.append(token)
    except IndentationError as e:
        try:
            _ignore, linenumber, col, line = e.args[1]
            type_ = py_tokenize.NAME  # Not really relevant what we set here
            # except that ERRORTOKEN would cause problems later on.
            start = (linenumber, col)
            end = (linenumber, len(line))
            string = line[col:].strip()
            token = Token((type_, string, start, end, line))
            tokens.append(token)
            return tokens
        except Exception as e:  # pragma: no cover
            debug_helper.log(
                "after IndentationError, error from token_utils.tokenize()"
            )
            debug_helper.log(repr(e))
            return tokens
    except (py_tokenize.TokenError, Exception):
        pass

    new_source = untokenize(tokens)
    if not source.strip():  # Used to prevent "fix" to be applied to
        return tokens  # MEANINGLESS_TOKEN defined elsewhere

    if new_source != source:
        length = len(new_source)
        remaining = source[length:]
        if not (
            remaining.lstrip().startswith(('"""', "'''"))
            or remaining.lstrip().startswith(("'", '"'))
        ):
            if sys.version_info >= (3, 12):
                tokens = handle_remaining(tokens, remaining)
            elif source.endswith((" ", "\t")):
                fix_empty_last_line(source, tokens)
            return tokens
        else:
            return add_unclosed_string_content(tokens, remaining, new_source)

    if source.endswith((" ", "\t")):
        fix_empty_last_line(source, tokens)

    return tokens


def add_unclosed_string_content(tokens, remaining, new_source):
    additional_lines = [line + "\n" for line in remaining.split("\n")]
    # removed extra \n added on last line
    additional_lines[-1] = additional_lines[-1][0:-1]
    last_token = tokens[-1]
    string = additional_lines[0]
    if new_source.endswith("\n"):
        start_row = last_token.end_row + 1
        start_col = 0
        end_col = len(string)
        line = string
    else:
        spaces_before_quotes = len(string) - len(string.lstrip())
        start_row = last_token.end_row
        start_col = last_token.end_col + spaces_before_quotes
        string = string.lstrip()
        end_col = start_col + len(string)
        line = last_token.string + string
    end_row = start_row
    tokens.append(
        Token((UNCLOSED, string, (start_row, start_col), (end_row, end_col), line))
    )
    for line in additional_lines[1:]:
        start_row += 1
        end_row = start_row
        start_col = 0
        end_col = len(line)
        tokens.append(
            Token(
                (
                    UNCLOSED,
                    line,
                    (start_row, start_col),
                    (end_row, end_col),
                    line,
                )
            )
        )
    return tokens


def handle_remaining(tokens, remaining):
    """With Python 3.12, the tokenizer changed significantly and can drop content
    when invalid code is encountered. This is an attempt to provide a
    sufficient fix for friendly-traceback. Note that this will not guarantee that

        source == untokenize(tokenize(source))

    but should be sufficient for providing the relevant information for
    SyntaxError cases.

    See https://github.com/friendly-traceback/friendly-traceback/issues/242.
    """
    rest_of_line = remaining.split("\n")[0]

    if not tokens:
        start_row = 1
        start_col = 0
        line = rest_of_line
    else:
        start_row, start_col = tokens[-1].end
        line = tokens[-1].line

    stripped_remaining = rest_of_line.lstrip()
    start_col += len(rest_of_line) - len(stripped_remaining)

    position = 0
    if stripped_remaining.startswith(("0o", "0O")):
        # find first offending digit
        for ch in stripped_remaining:
            if ch in {"8", "9"}:
                break
            position += 1
        else:
            debug_helper.log("Did not find disallowed octal digit")
            return tokens

    tokens.append(
        Token(
            (
                py_tokenize.NUMBER,
                stripped_remaining[:position],
                (start_row, start_col),
                (start_row, start_col + position),
                line,
            )
        )
    )
    source_rest = rest_of_line[position + 1 :]

    remaining_tokens = tokenize(source_rest)
    for tok in remaining_tokens:
        if not tok.string:
            tok.line = ""
        else:
            tok.line = line
        if tok.start_col == 0 and tok.string == "":  # Endmarker
            tok.start = tok.end = (tok.start_row, tok.start_col) = (
                tok.end_row,
                tok.end_col,
            ) = (start_row + 1, 0)
        else:
            tok.start = (tok.start_row, tok.start_col) = (
                start_row,
                tok.start_col + start_col + position,
            )
            tok.end = (tok.end_row, tok.end_col) = (
                start_row,
                tok.end_col + start_col + position,
            )
        tokens.append(tok)

    return tokens


def get_significant_tokens(source: str) -> List[Token]:
    """Gets a list of tokens from a source (str), ignoring comments
    as well as any token whose string value is either null or
    consists of spaces, newline or tab characters.
    """
    try:
        tokens = tokenize(source)
    except Exception as e:  # pragma: no cover
        debug_helper.log("Exception from token_utils.get_significant_tokens()")
        debug_helper.log_error(e)
        return []
    return remove_meaningless_tokens(tokens)


def remove_meaningless_tokens(tokens: Iterable[Token]) -> List[Token]:
    """Given a list of tokens, remove all space-like tokens and comments."""
    new_tokens = []
    for tok in tokens:
        if not tok.string.strip() or tok.is_comment():
            continue
        new_tokens.append(tok)
    return new_tokens


def get_lines(source: str) -> List[List[Token]]:
    """Transforms a source (string) into a list of Tokens, with each
    (inner) list containing all the tokens found on a given line of code.
    """
    lines: List[List[Token]] = []
    current_row = -1
    new_line: List[Token] = []
    tokens = tokenize(source)
    if not tokens:
        return [[]]
    new_line = [tokens[0]]

    for token in tokens[1:]:
        if token.start_row != current_row:
            current_row = token.start_row
            if new_line:
                lines.append(new_line)
            new_line = []
        new_line.append(token)
    lines.append(new_line)

    return lines


def strip_comment(line: str) -> str:
    """Removes comments from a line"""
    tokens = []
    try:
        for tok in py_tokenize.generate_tokens(StringIO(line).readline):
            token = Token(tok)
            if token.is_comment():
                continue
            if not token.string:
                token.line = ""
            tokens.append(token)
    except py_tokenize.TokenError:
        pass
    return untokenize(tokens)


def find_substring_index(main: str, substring: str) -> int:
    """Somewhat similar to the find() method for strings,
    this function determines if the tokens for substring appear
    as a subsequence of the tokens for main. If so, the index
    of the first token in returned, otherwise -1 is returned.
    """
    main_tokens = [tok.string for tok in get_significant_tokens(main)]
    sub_tokens = [tok.string for tok in get_significant_tokens(substring)]
    for index, token in enumerate(main_tokens):
        if token == sub_tokens[0]:
            for i, tok in enumerate(main_tokens[index : index + len(sub_tokens)]):
                if tok != sub_tokens[i]:
                    break
            else:
                return index
    return -1


def dedent(tokens: Iterable[Union[str, Token]], nb: int) -> List[Token]:
    """Given a list of tokens, produces an equivalent list corresponding
    to a line of code with the first nb characters removed.
    """
    line = untokenize(tokens)
    line = line[nb:]
    return tokenize(line)


def indent(
    tokens: Iterable[Union[str, Token]], nb: int, tab: bool = False
) -> List[Token]:
    """Given a list of tokens, produces an equivalent list corresponding
    to a line of code with nb space characters inserted at the beginning.

    If ``tab`` is specified to be ``True``, ``nb`` tab characters are inserted
    instead of spaces.
    """
    line = untokenize(tokens)
    line = "\t" * nb + line if tab else " " * nb + line
    return tokenize(line)


def untokenize(tokens: Iterable[Union[str, Token]]) -> str:
    """Return source code based on tokens.

    This is similar to Python's own tokenize.untokenize(), except that it
    preserves spacing between tokens, by using the line
    information recorded by Python's tokenize.generate_tokens.
    As a result, if the original source code had multiple spaces between
    some tokens or if escaped newlines were used or if tab characters
    were present in the original source, those will also be present
    in the source code produced by untokenize.

    Thus ``source == untokenize(tokenize(source))``.

    Note: if you you modifying tokens from an original source:

    Instead of full token object, ``untokenize`` will accept simple
    strings; however, it will only insert them *as is* without taking them
    into account when it comes with figuring out spacing between tokens.
    """
    # Adapted from https://github.com/myint/untokenize,
    # Copyright (C) 2013-2018 Steven Myint, MIT License (same as this project).

    words = []
    previous_line = ""
    last_row = 0
    last_column = -1
    last_non_whitespace_token_type = None

    for token in tokens:
        if isinstance(token, str):  # pragma: no cover
            words.append(token)
            continue
        if token.type == py_tokenize.ENCODING:  # pragma: no cover
            continue

        # Preserve escaped newlines.
        if (
            last_non_whitespace_token_type != py_tokenize.COMMENT
            and token.start_row > last_row
            and previous_line.endswith(("\\\n", "\\\r\n", "\\\r"))
        ):
            words.append(previous_line[len(previous_line.rstrip(" \t\n\r\\")) :])

        # Preserve spacing.
        if token.start_row > last_row:
            last_column = 0
        if token.start_col > last_column:
            words.append(token.line[last_column : token.start_col])

        words.append(token.string)

        previous_line = token.line
        last_row = token.end_row
        last_column = token.end_col
        if not token.is_space():
            last_non_whitespace_token_type = token.type

    return "".join(words)


TextOrTokens = Union[str, Sequence[Union[str, Token]]]


def print_tokens(source: TextOrTokens) -> None:  # pragma: no cover
    """Prints tokens found in source, excluding spaces and comments.

    ``source`` is either a string to be tokenized, or a list of Token objects.

    This is occasionally useful as a debugging tool.
    """
    if isinstance(source[0], Token):
        source = untokenize(source)

    for lines in get_lines(source):  # type: ignore
        for token in lines:
            print(repr(token))
        print()
