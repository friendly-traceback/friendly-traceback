from _typeshed import Incomplete

import re
import traceback
import types
from typing import List, Optional, Type
from . import debug_helper, info_generic, info_variables, message_parser, tb_data
from .frame_info import FrameInfo
from .ft_gettext import current_lang
from .path_info import path_utils
from .source_cache import cache
from .syntax_errors import analyze_syntax, indentation_error
from .typing_info import _E, Info
import executing

TracebackData: type[TracebackData]


class FriendlyTraceback:
    info: Info
    message: str
    suppressed: list[str]
    tb: TracebackType
    tb_data: Incomplete

    def __init__(self, etype: Type[_E], value: _E, tb: types.TracebackType) -> None: ...

    def assign_message(self, etype: Incomplete, value: Incomplete) -> str: ...

    def compile_info(self) -> None: ...

    def recompile_info(self) -> None: ...

    def add_exception_note(self) -> Incomplete: ...

    def assign_cause(self) -> None: ...

    def set_cause_runtime(self) -> None: ...

    def set_cause_syntax(self) -> None: ...

    def assign_generic(self) -> None: ...

    def assign_location(self) -> None: ...

    def locate_exception_raised(self, record: FrameInfo) -> None: ...

    def locate_last_call(self, record: FrameInfo, partial_source: Incomplete, var_info: Incomplete) -> None: ...

    def get_detailed_stack_info(self) -> Incomplete: ...

    def locate_parsing_error(self) -> None: ...

    def assign_tracebacks(self) -> None: ...

    def shorten(self, tb: List[str]) -> List[str]: ...

    def create_traceback(self, records: List[FrameInfo]) -> List[str]: ...


def process_exception_chain(etype: Type[_E], value: _E) -> str: ...


def cannot_analyze_stdin() -> str: ...
