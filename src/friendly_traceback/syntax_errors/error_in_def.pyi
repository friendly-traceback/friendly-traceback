from typing import Literal
from _typeshed import Incomplete

import platform
import sys
from .. import debug_helper, utils
from ..ft_gettext import current_lang, internal_error
from . import fixers
from . import syntax_utils as su

STATEMENT_ANALYZERS: Incomplete
ASYNC: Literal[0] = 0


def more_errors() -> Incomplete: ...


def def_correct_syntax() -> Incomplete: ...


def add_statement_analyzer(func: Incomplete) -> Incomplete: ...


def analyze_def_statement(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def def_begin_code_block(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_parens(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_parens_2(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def missing_colon(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def keyword_as_function_name(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def other_invalid_function_names(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def function_definition_missing_name(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def keyword_not_allowed_as_function_argument(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def dotted_name_not_allowed(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def positional_arguments_in_def(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def keyword_arguments_in_def(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def number_as_argument(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def string_as_argument(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def tuple_as_argument(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def list_as_argument(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def dict_or_set_as_argument(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def operator_as_argument(statement: Incomplete) -> Incomplete: ...


@add_statement_analyzer
def arg_after_kwarg(statement: Incomplete) -> Incomplete: ...
