"""utils.py

A few useful objects which do not naturally fit anywhere else.
"""
import ast
import difflib
import types
import uuid
from typing import TYPE_CHECKING, Any, Iterable, List, Tuple, Union

import executing
import pure_eval

from . import debug_helper
from .ft_gettext import internal_error, no_information, unknown_case
from .typing import CauseInfo, Parser

if TYPE_CHECKING:
    from .core import TracebackData


class RuntimeMessageParser:
    """Used to collect message parsers and cycle through them in
    an attempt at finding the cause of an exception.
    """

    def __init__(self) -> None:
        self.parsers: List[Parser] = []
        self.current_parser: Parser = None

    def add(self, func: Parser) -> None:
        """Use as a decorator to add a message parser"""
        self.parsers.append(func)

    def get_cause(
        self,
        value_or_message: Union[str, BaseException],
        frame: types.FrameType,
        tb_data: "TracebackData",
    ) -> CauseInfo:
        """Called from info_specific.py where, depending on error type,
        the value could be converted into a message by calling str().
        """
        try:
            return self._get_cause(value_or_message, frame, tb_data)
        except Exception as e:  # noqa # pragma: no cover
            debug_helper.log(f"Problem with {self.current_parser.__name__}")
            debug_helper.log(f"in module {self.current_parser.__module__}")
            return {"cause": internal_error(e), "suggest": internal_error(e)}

    def _get_cause(
        self,
        value_or_message: Union[str, BaseException],
        frame: types.FrameType,
        tb_data: "TracebackData",
    ) -> CauseInfo:
        """Cycle through the parsers, looking for one that can find a cause."""
        for self.current_parser in self.parsers:
            # This could be simpler if we could use the walrus operator
            cause = self.current_parser(value_or_message, frame, tb_data)
            if cause:
                return cause
        return {"cause": no_information(), "suggest": unknown_case()}


def unique_variable_name() -> str:
    """Creates a unique variable name. Useful when attempting to introduce
    a new token to see if it can fix specific cases of SyntaxError."""
    name = uuid.uuid4()
    return "_%s" % name.hex


def eval_expr(expr: str, frame: types.FrameType) -> Any:
    """Attempts to evaluate the expression 'expr' in a frame.
    Note that 'expr' might be a string containing leading spaces which need
    to be removed prior to being evaluated.

    This can raise some exceptions which are meant to be caught by the
    calling function.
    """
    node = ast.parse(expr.strip()).body[0].value  # noqa
    evaluator = pure_eval.Evaluator.from_frame(frame)
    return evaluator[node]  # can raise an exception


def get_similar_words(word_with_typo: str, words: Iterable[str]) -> List[str]:
    """Returns a list of similar words.

    The parameters we chose are based on experimenting with
    different values of the cutoff parameter for the difflib function
    get_close_matches.

    Suppose we have the following words:
    ['cos', 'cosh', 'acos', 'acosh']
    If we use a cutoff of 0.66, and ask for a maximum of 4 matches,
    all will be a match for 'cost'.  However, if we increase the cutoff
    to 0.67, 'acosh' will be dropped from the list, which seems sensible.

    However, this cutoff is "too generous" when dealing with long words.
    Using a cutoff up to 0.75 will result in both 'ascii_lowercase'
    and 'ascii_uppercase' matching 'ascii_lowecase'. Increasing the cutoff
    to 0.76 will drop ascii_uppercase as a match which also seems sensible.

    We thus use a heuristic cutoff based on length which ends up
    matching our expectation as to what a close match should be.

    We also do not return any matches for single character variables,
    nor do we consider single character variable potential matches.
    """
    if len(word_with_typo) == 1:
        return []
    words = set(words)
    words = [word for word in words if len(word) > 1]

    get = difflib.get_close_matches

    cutoff = min(0.8, 0.63 + 0.01 * len(word_with_typo))
    if len(word_with_typo) > 2:
        result = get(word_with_typo, words, n=5, cutoff=cutoff)
        if result:
            return result
    # In the absence of results, we try see if the typos could have been
    # caused by using the wrong case; this works well also
    # for words of length 2, such as writing Pi instead of pi.
    result = get(word_with_typo.casefold(), words, n=1, cutoff=cutoff)
    if result:
        return result
    result = get(word_with_typo.upper(), words, n=1, cutoff=cutoff)
    if result:
        return result

    # Finally, for words of length 2, such as writing 'it' instead of 'if',
    # we lower the cutoff but make sure that the matched words
    # are not too long: difflib finds that 'with' is much more similar to
    # 'it' than 'if' would be!
    if len(word_with_typo) == 2:
        cutoff = 0.5
        words = [word for word in words if len(word) <= 3]
        result = get(word_with_typo, words, n=5, cutoff=cutoff)
    return result


def list_to_string(list_: Iterable[str], sep: str = ", ") -> str:
    """Transforms a list of names, like ['a', 'b', 'c'], into a single
    string of names, like "a, b, c"."""
    result = ["{c}".format(c=c.replace("'", "")) for c in list_]
    return sep.join(result)


def expected_in_result(expected: str, result: str) -> Tuple[bool, str]:
    """Used in tests. Intended to help more quickly identify
    differences between what was expected and what was found."""
    if expected in result:
        return True, "Test is satisfied: 'expected' is found in 'result'."
    result = result.strip(" ")
    lines = result.splitlines()
    best_ratio = 0.0
    best_line = ""
    for line in lines:
        line = line.strip(" ")
        ratio = difflib.SequenceMatcher(None, expected, line).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_line = line

    if result == best_line:
        return False, "Only differences are different white spaces at the ends."

    return False, "\n" + "\n".join(difflib.ndiff([expected], [best_line]))


def get_bad_statement(tb_data: "TracebackData") -> str:
    """This function attempts to recover a complete statement
    even if it spans multiple lines."""
    try:
        st = executing.executing.statement_containing_node(tb_data.node)
        source = executing.executing.Source.for_frame(tb_data.exception_frame)
        return source.asttokens().get_text(st)
    except Exception:  # noqa
        if hasattr(tb_data, "original_bad_line"):
            return tb_data.original_bad_line
        elif hasattr(tb_data, "bad_line"):
            return tb_data.bad_line
        return ""
