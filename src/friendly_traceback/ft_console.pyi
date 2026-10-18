from _typeshed import Incomplete

import types
from code import InteractiveConsole
from typing import Any, Callable, Mapping, Optional, Union, Protocol, TypedDict, List
from friendly_traceback.base_formatters import InclusionChoice
from friendly_traceback.tb_data import TracebackData

class Info(TypedDict, total=False):
    header: str
    message: str
    original_python_traceback: str
    simulated_python_traceback: str
    shortened_traceback: str
    exception_notes_intro: List[str]
    exception_notes: str
    suggest: str
    generic: str
    parsing_error: str
    parsing_error_source: str
    cause: str
    detailed_tb: List[str]
    last_call_header: str
    last_call_source: str
    last_call_variables: str
    exception_raised_header: str
    exception_raised_source: str
    exception_raised_variables: str
    warning_message: str
    warning_location_header: str
    warning_source: str
    warning_variables: str
    additional_variable_warning: str
    lang: str
    _tb_data: TracebackData

class Formatter(Protocol):
    def __call__(self, info: Info, include: InclusionChoice = ...) -> str: ...

def type_friendly() -> str: ...

BANNER: str

def rich_displayhook(value: Any) -> None: ...
def toggle_prompt() -> None: ...

class FriendlyTracebackConsole(InteractiveConsole):
    counter: int
    fake_filename: str

    def __init__(
        self,
        local_vars: Optional[Mapping[str, Any]] = None,
        formatter: Union[str, Formatter] = "repl",
        displayhook: Optional[Callable[[object], Any]] = None,
        ipython_prompt: bool = True,
    ) -> None: ...
    def interact(
        self, banner: Incomplete = None, exitmsg: Incomplete = None
    ) -> None: ...
    def push(self, line: str) -> bool: ...
    def runsource(
        self, source: str, filename: str = "<friendly-console>", symbol: str = "single"
    ) -> bool: ...
    def runcode(self, code: types.CodeType) -> None: ...
    def showsyntaxerror(self, filename: Optional[str] = None) -> None: ...
    def showtraceback(self) -> None: ...

def start_console(
    local_vars: Optional[Mapping[str, Any]] = None,
    formatter: Union[str, Formatter] = "repl",
    include: InclusionChoice = "friendly_tb",
    lang: str = "en",
    banner: Optional[str] = None,
    displayhook: Optional[Callable[[object], Any]] = None,
    ipython_prompt: bool = True,
) -> None: ...
