from _typeshed import Incomplete

import unicodedata
from .. import debug_helper, token_utils
from ..ft_gettext import current_lang


def matching_brackets(bra: Incomplete, ket: Incomplete) -> Incomplete: ...


def name_bracket(bracket: Incomplete) -> Incomplete: ...


bad_quotation_marks: list[str]


def identify_bad_quote_char(char: Incomplete, line: Incomplete) -> Incomplete: ...


def identify_bad_math_symbol(char: Incomplete, line: Incomplete) -> Incomplete: ...


def identify_unicode_fraction(char: Incomplete) -> Incomplete: ...


def highlight_single_token(token: Incomplete) -> Incomplete: ...


def highlight_added_token(prev_token: Incomplete, token: Incomplete) -> Incomplete: ...


def highlight_two_tokens(first: Incomplete, second: Incomplete, first_marker: Incomplete = "^", second_marker: Incomplete = "^", between: Incomplete = " ") -> Incomplete: ...


def highlight_range(first: Incomplete, last: Incomplete) -> Incomplete: ...


def get_last_token_before_specified(bad_token: Incomplete, tokens: Incomplete, specified_token: Incomplete) -> Incomplete: ...


def highlight_before_specified_token(bad_token: Incomplete, tokens: Incomplete, specified_token: Incomplete) -> Incomplete: ...


def get_expression_before_specified_token(bad_token: Incomplete, tokens: Incomplete, specified_token: Incomplete) -> Incomplete: ...


def add_mark_to_new_statement(statement_object: Incomplete, new_statement: Incomplete, mark: Incomplete) -> Incomplete: ...
