from _typeshed import Incomplete

import keyword
import sys
from .. import debug_helper, token_utils, utils
from ..ft_gettext import current_lang, internal_error
from . import error_in_def, fixers
from . import syntax_utils as su

STATEMENT_ANALYZERS: Incomplete


def more_errors() -> Incomplete: ...


def add_statement_analyzer(func: Incomplete) -> Incomplete: ...


def analyze_statement(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def invalid_non_printable_character(statement: Incomplete = None) -> Incomplete: ...


@add_statement_analyzer
def missing_index(statement: Incomplete = None) -> Incomplete: ...


@add_statement_analyzer
def mismatched_brackets(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def copy_pasted_code(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def detect_backquote(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def wrong_code_block(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def keyword_as_attribute(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def confused_elif(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def import_from(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def misplaced_quote(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def detect_walrus(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def inverted_operators(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def consecutive_operators(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def walrus_instead_of_equal(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def assign_instead_of_equal(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def print_as_statement(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def calling_python_or_pip(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def dot_followed_by_bracket(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def raise_single_exception(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def invalid_double_star_operator(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_colon(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def semi_colon_instead_of_comma(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def semi_colon_instead_of_colon(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def invalid_hexadecimal(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def invalid_octal(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def invalid_name(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def debug_fstring(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def general_fstring_problem(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def assign_to_a_keyword(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def lambda_with_paren(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def wrong_type_declaration(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_comma_before_string_in_dict(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_in_with_for(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_parens_for_range(statement: Incomplete) -> Incomplete: ...


def misspelled_python_keyword(tokens: Incomplete, bad_token: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def comprehension_condition_or_tuple(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def parens_around_exceptions(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def current_is_misspelled_python_keyword(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def previous_is_misspelled_python_keyword(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def space_in_variable_name(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def impossible_binary_fstring(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_comma_or_operator(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def equal_instead_of_colon_in_dict(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def boolean_instead_of_comma(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def from_import_as(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def delete_names_or_items(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def duplicate_token(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def extra_token(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_value_in_dict(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def else_with_no_match(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def elif_with_no_matching_if(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def except_with_no_matching_try(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def finally_with_no_matching_try(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def bracket_instead_of_paren(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def unclosed_bracket(statement: Incomplete) -> Incomplete: ...
