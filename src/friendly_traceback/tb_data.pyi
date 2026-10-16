from typing import Literal
from _typeshed import Incomplete

import contextlib
import inspect
import io
import sys
import traceback
import types
from itertools import dropwhile
from typing import Generic, List, Optional, Tuple, Type
from stack_data import BlankLines, Options
from . import debug_helper
from .frame_info import FrameInfo
from .ft_gettext import current_lang
from .path_info import is_excluded_file
from .source_cache import cache
from .syntax_errors import source_info
from .typing_info import _E

STR_FAILED: Literal['<exception str() failed>'] = "<exception str() failed>"


def convert_value_to_message(value: BaseException) -> str: ...


def retrieve_message(etype: Type[_E], value: _E, tb: types.TracebackType) -> str: ...


class TracebackData(Generic[_E]):
    bad_line: str
    exception_frame: FrameType | None
    exception_instance: _E | None
    exception_name: str
    exception_type: type[_E]
    filename: str
    formatted_tb: list[str]
    full_message: str
    message: str
    node: Incomplete
    node_range: tuple[int, int] | None
    node_text: str
    original_bad_line: str
    program_stopped_bad_line: str
    program_stopped_frame: FrameType | None
    program_stopped_node_range: Incomplete
    python_records: list[FrameInfo]
    records: list[FrameInfo]
    simulated_python_traceback: str | None
    statement: Statement | None
    value: _E

    def __init__(self, etype: Type[_E], value: _E, tb: types.TracebackType) -> None: ...

    def get_records(self, tb: types.TracebackType, python_excluded: bool = True) -> List[FrameInfo]: ...

    def get_source_info(self) -> None: ...

    def locate_error(self) -> None: ...
