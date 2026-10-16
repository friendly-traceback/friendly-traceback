from _typeshed import Incomplete

import __future__
import ast
import re
import sys
from .. import debug_helper, token_utils, utils
from ..ft_gettext import current_lang, please_report
from . import error_in_def, fixers, statement_analyzer
from . import syntax_utils as su

MESSAGE_ANALYZERS: Incomplete


def add_python_message(func: Incomplete) -> Incomplete: ...


def analyze_message(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_conditional_expression(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_expression(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_function_call(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_generator_expression(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_f_expression(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_keyword(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_literal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_operator(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_yield_expression(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assignment_cannot_rebind_inside_comprehension(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assignment_cannot_rebind_inside_comprehension_inner_loop(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def annotated_name_cannot_be_global(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def augmented_assignment_with_literal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def both_nonlocal_and_global(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def bracket_was_expected(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def break_outside_loop(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_assign_to_attribute(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_delete_constant(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_delete_expression(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_delete_function_call(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_delete_literal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_delete_named_expression(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_use_starred_expression(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def colon_expected(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def colon_missing_after_dict_key(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def continue_outside_loop(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def duplicate_argument_in_function_definition(message: str = "", statement: Incomplete = None) -> Incomplete: ...


def locate_duplicate_arguments(statement: Incomplete, name: Incomplete) -> Incomplete: ...


@add_python_message
def else_after_if(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def eof_unclosed_triple_quoted(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def eol_while_scanning_string_literal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def expected_except_or_finally(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def expected_paren(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def expression_cannot_contain_assignment(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def expression_missing_after_dict_key_and_colon(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def f_string_backslash(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def f_string_curly_not_allowed(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def f_string_expecting_curly(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def forgot_paren_around_comprehension(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def from__future__at_begin(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def from__future__not_defined(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def function_parameters_cannot_be_paren(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def generator_expression_must_be_parenthesized(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def import_braces(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_character_in_identifier(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_decimal_literal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_double_star_operator(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_hexadecimal_literal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_imaginary_literal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_octal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def iterable_unpacking_cannot_be_used_in_comprehension(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_token(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def keyword_argument_repeated(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def lambda_expression_parameters_cannot_be_paren(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def leading_zeros_in_decimal_integers(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def mismatched_parenthesis(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def named_arguments_must_follow_bare_star(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def name_assigned_to_prior_global(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def name_assigned_to_prior_nonlocal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def name_is_parameter_and_global(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def name_is_parameter_and_nonlocal(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def name_used_prior_global(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def name_used_prior_nonlocal(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def no_binding_for_nonlocal(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def nonlocal_at_module_level(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def non_default_arg_follows_default_arg(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def parens_around_exceptions(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def positional_argument_follows_keyword_arg(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def python2_print(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def return_outside_function(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def star_assignment_target_must_be_list(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def starred_expression_in_dict_value(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def too_many_nested_blocks(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def too_many_nested_parenthesis(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def trailing_comma_not_allowed(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def unexpected_character_after_continuation(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def unexpected_eof_while_parsing(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def unicode_error(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def unmatched_parenthesis(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def unterminated_f_string(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def yield_outside_function(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def you_found_it(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def cannot_delete_something_else(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def assign_to_others(message: str = "", _statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def arguments_cannot_follow_var(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def slash_must_be_ahead(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def star_may_appear_only_once(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def slash_must_appear_only_once(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def invalid_non_printable_character(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def import_from(message: str = "", statement: Incomplete = None) -> Incomplete: ...


@add_python_message
def incomplete_input(message: str = "", statement: Incomplete = None) -> Incomplete: ...
