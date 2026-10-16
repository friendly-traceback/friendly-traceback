from _typeshed import Incomplete

import os
from typing import Iterable
import stack_data
from executing import only
from stack_data import LINE_GAP, BlankLineRange, BlankLines, Formatter, Line, Options
from stack_data.utils import cached_property
from friendly_traceback import token_utils
from . import debug_helper
from .ft_gettext import current_lang
from .source_cache import cache


class FriendlyFormatter(Formatter):
    indent: str

    def __init__(self, **kwargs: Incomplete) -> Incomplete: ...

    def format_frame_source(self, frame: stack_data.FrameInfo) -> Iterable[str]: ...

    def format_line(self, line: Line) -> str: ...

    def format_blank_lines_linenumbers(self, blank_line: Incomplete) -> Incomplete: ...


class FrameInfo(stack_data.FrameInfo):
    @cached_property
    def partial_source(self) -> str: ...

    @cached_property
    def partial_source_with_node_range(self) -> str: ...

    @cached_property
    def highlighted_source(self) -> str: ...

    def problem_line(self) -> str: ...

    @cached_property
    def node_info(self) -> Incomplete: ...

    @cached_property
    def current_line(self) -> Incomplete: ...

    def handle_special_cases(self) -> str: ...


class FakeLineObject:
    is_current: Incomplete
    lineno: Incomplete
    text: Incomplete

    def __init__(self, line: Incomplete, linenumber: Incomplete, lineno: Incomplete) -> Incomplete: ...

    def __repr__(self) -> Incomplete: ...
