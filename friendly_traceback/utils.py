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
from .typing_info import CauseInfo, Parser

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
        debug_helper.log_2(str(value_or_message))
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
    words = set(words)  # removes duplicates
    words = sorted(list(words))  # get predictable order for tests

    if 2 <= len(word_with_typo) <= 4:
        words = [word for word in words if 2 <= len(word) <= 5]
        max_dist = 1
    elif 5 <= len(word_with_typo) <= 8:
        words = [word for word in words if 4 <= len(word) <= 10]
        max_dist = 2
    else:
        words = [word for word in words if len(word) >= 7]
        max_dist = 3

    similar_words = {}
    for word in words:
        distance = _leven(word_with_typo, word, max_dist + 1)
        if distance <= max_dist:
            if distance in similar_words:
                similar_words[distance].append(word)
            else:
                similar_words[distance] = [word]

    similar = []
    for distance in range(1, max_dist + 1):
        if distance in similar_words and similar_words[distance]:
            similar.extend(similar_words[distance])
    if not similar:  # example PI -> pi
        if word_with_typo.lower() in words:
            similar.append(word_with_typo.lower())
        elif word_with_typo.upper() in words:
            similar.append(word_with_typo.upper())
    return similar


# The following code, including comments, has been adapted from
# https://gist.github.com/giststhebearbear/4145811


def _leven(s1, s2, max_distance):
    #  get smallest string so our rows are minimized
    s1, s2 = (s1, s2) if len(s1) <= len(s2) else (s2, s1)
    #  set lengths
    l1, l2 = len(s1), len(s2)

    #  We are simulating an NM matrix where n is the longer string
    #  and m is the shorter string. By doing this we can minimize
    #  memory usage to O(M).
    #  Since we are simulating the matrix we only maintain two rows
    #  at a time the current row and the previous rows.
    #  A move from the current cell looking at the cell before it indicates
    #  consideration of an insert operation.
    #  A move from the current cell looking at the cell above it indicates
    #  consideration of a deletion
    #  Both operations are cost 1
    #  A move from the current cell to the cell up and to the left indicates
    #  an edit operation of 0 cost for a matching character and a 1 cost for
    #  a non matching characters
    #  no row has been previously computed yet, set empty row
    #  Since this is also a Damerau-Levenshtein calculation transposition
    #  costs will be taken into account. These look back 2 characters to
    #  determine optimal cost based on a possible transposition
    #  example: aei -> aie with Levensthein has a cost of 2
    #  match a, change e->i change i->e => aie
    #  Damarau-Levenshtein has a cost of 1
    #  match a, transpose ei to ie => aie
    prev_row = None

    #  build first leven matrix row
    #  The first row represents transformation from an empty string
    #  to the shorter string making it static [0-n]
    #  since this row is static we can set it as
    #  cur_row and start computation at the second row or index 1
    cur_row = [x for x in range(l1 + 1)]

    # use second length to loop through all the rows being built
    # we start at row one
    for row_num in range(1, l2 + 1):
        #  set transposition, previous, and current
        #  because the row_num always increments by one
        #  we can use row_num to set the value representing
        #  the first column which is indicative of transforming TO
        #  the empty string from our longer string
        #  transposition row maintains an extra row so that it is possible
        #  for us to apply Damarau's formula
        transposition_row, prev_row, cur_row = prev_row, cur_row, [row_num] + [0] * l1

        #  consider if we have passed the max distance if all paths through
        #  the transposition row are larger than the max we can stop calculating
        #  distance and return the last element in that row and return the max
        if transposition_row and all(
            cell_value > max_distance for cell_value in transposition_row
        ):
            return max_distance

        for col_num in range(1, l1 + 1):
            insertion_cost = cur_row[col_num - 1] + 1
            deletion_cost = prev_row[col_num] + 1
            change_cost = prev_row[col_num - 1] + (
                0 if s1[col_num - 1] == s2[row_num - 1] else 1
            )
            #  set the cell value - min distance to reach this
            #  position
            cur_row[col_num] = min(insertion_cost, deletion_cost, change_cost)

            #  test for a possible transposition optimization
            #  check to see if we have at least 2 characters
            if 1 < row_num <= col_num:  # sourcery skip
                #  test for possible transposition
                if (
                    s1[col_num - 1] == s2[col_num - 2]
                    and s2[col_num - 1] == s1[col_num - 2]
                ):
                    cur_row[col_num] = min(
                        cur_row[col_num], transposition_row[col_num - 2] + 1
                    )

    #  the last cell of the matrix is ALWAYS the shortest distance between the two strings
    return cur_row[-1]


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


def to_code_block(code: str) -> str:
    """Takes some code and indent it with an added empty line at the top
    and bottom so that it is usable as a Markdown code block without
    showing the triple backquotes.
    """
    indent = " " * 4
    new_lines = ["\n"]
    lines = code.split("\n")
    for line in lines:
        new_lines.append(f"{indent}{line}")
    new_lines.append("\n")
    return "\n".join(new_lines)
