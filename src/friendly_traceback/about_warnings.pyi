from _typeshed import Incomplete

from typing import List, Type
from stack_data import Formatter
from .typing_info import CauseInfo, Parser

IGNORE_WARNINGS: Incomplete

def enable_warnings(testing: bool = False) -> None: ...

class MyFormatter(Formatter):
    def format_frame(self, frame: Incomplete) -> Incomplete: ...

class WarningInfo:
    begin_lineno: Incomplete
    filename: Incomplete
    frame: Incomplete
    info: dict[str, str]
    lineno: Incomplete
    lines: Incomplete
    message: str
    problem_statement: str
    warning_instance: Incomplete
    warning_type: Incomplete

    def __init__(
        self,
        warning_instance: Incomplete,
        warning_type: Incomplete,
        filename: Incomplete,
        lineno: Incomplete,
        frame: Incomplete = None,
        lines: Incomplete = None,
    ) -> None: ...
    def recompile_info(self) -> Incomplete: ...
    def format_source(self) -> Incomplete: ...
    def get_source_frame_missing(self) -> Incomplete: ...

def saw_warning_before(
    warning_type: Incomplete,
    message: Incomplete,
    filename: Incomplete,
    lineno: Incomplete,
) -> bool: ...
def show_warning(
    warning_instance: Incomplete,
    warning_type: Incomplete,
    filename: Incomplete,
    lineno: Incomplete,
    file: Incomplete = None,
    line: Incomplete = None,
) -> Incomplete: ...

INCLUDED_PARSERS: dict[type[SyntaxWarning], str]
WARNING_DATA_PARSERS: dict[type[BaseException], WarningDataParser]

class WarningDataParser:
    core_parsers: List[Parser]
    custom_parsers: List[Parser]
    parsers: List[Parser]

    def __init__(self) -> None: ...
    def add(self, func: Parser) -> None: ...

def get_warning_parser(warning_type: Type[BaseException]) -> WarningDataParser: ...
def get_warning_cause(
    warning_type: Incomplete,
    message: str,
    warning_data: WarningDataParser | None = None,
) -> CauseInfo: ...
def get_cause(
    warning_type: Incomplete, message: str, warning_data: WarningDataParser
) -> CauseInfo: ...
