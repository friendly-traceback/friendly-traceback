from _typeshed import Incomplete

from friendly_traceback.ft_gettext import current_lang, internal_error, unknown_case
from .. import debug_helper
from . import message_analyzer, statement_analyzer


def unknown_cause() -> Incomplete: ...


def set_cause_syntax(value: Incomplete, tb_data: Incomplete) -> Incomplete: ...


def find_syntax_error_cause(value: Incomplete, tb_data: Incomplete) -> Incomplete: ...
