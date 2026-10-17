from types import FrameType
from typing import List, Type, Set, Dict, Iterable
from stack_data import Formatter  # pyright: ignore[reportMissingImports]
from .typing_info import CauseInfo, Parser

def enable_warnings(testing: bool = False) -> None: ...

class MyFormatter(Formatter):
    def format_frame(self, frame: FrameType) -> Iterable[str]: ...

class WarningInfo:
    begin_lineno: int
    filename: str
    frame: FrameType
    info: dict[str, str]
    lineno: int
    lines: List[str]
    message: str
    problem_statement: str
    warning_instance: Warning
    warning_type: type[Warning]

    def __init__(
        self,
        warning_instance: Warning,
        warning_type: type[Warning],
        filename: str,
        lineno: int,
        frame: FrameType | None = None,
        lines: List[str] | None = None,
    ) -> None: ...
    def recompile_info(self) -> None: ...
    def format_source(self) -> str: ...
    def get_source_frame_missing(self) -> None: ...

def saw_warning_before(
    warning_type: type[Warning],
    message: str,
    filename: str,
    lineno: int,
) -> bool: ...
def show_warning(
    warning_instance: Warning,
    warning_type: type[Warning],
    filename: str,
    lineno: int,
    file: str | None = None,
    line: int | None = None,
) -> None: ...

INCLUDED_PARSERS: dict[type[SyntaxWarning], str]
WARNING_DATA_PARSERS: dict[type[BaseException], WarningDataParser]

class WarningDataParser:
    core_parsers: List[Parser]
    custom_parsers: List[Parser]
    parsers: List[Parser]

    def __init__(self) -> None: ...
    def _add(self, func: Parser) -> None: ...
    def add(self, func: Parser) -> None: ...

def get_warning_parser(warning_type: Type[BaseException]) -> WarningDataParser: ...
def get_warning_cause(
    warning_type: type[Exception],
    message: str,
    warning_data: WarningDataParser | None = None,
) -> CauseInfo: ...
def get_cause(
    warning_type: type[Exception], message: str, warning_data: WarningDataParser
) -> CauseInfo: ...
