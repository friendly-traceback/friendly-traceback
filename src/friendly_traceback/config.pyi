from .ft_gettext import current_lang
from .typing_info import _E, Formatter, InclusionChoice, Info, Writer

session: _State

def did_exception_occur_before() -> bool: ...
