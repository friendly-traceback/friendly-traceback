from _typeshed import Incomplete

import codeop
import os
import platform
import sys
import traceback
import types
from code import InteractiveConsole
from typing import Any, Callable, Mapping, Optional, Union
import friendly_traceback
from . import source_cache
from .config import did_exception_occur_before, session
from .console_helpers import friendly_tb, helpers
from .ft_gettext import current_lang
from .typing_info import Formatter, InclusionChoice


def type_friendly() -> str: ...


BANNER: str


def rich_displayhook(value: Any) -> None: ...


def toggle_prompt() -> None: ...


class FriendlyTracebackConsole(InteractiveConsole):
    counter: int
    fake_filename: str

    def __init__(self, local_vars: Optional[Mapping[str, Any]] = None, formatter: Union[str, Formatter] = "repl", displayhook: Optional[Callable[[object], Any]] = None, ipython_prompt: bool = True) -> None: ...

    def interact(self, banner: Incomplete = None, exitmsg: Incomplete = None) -> None: ...

    def push(self, line: str) -> bool: ...

    def runsource(self, source: str, filename: str = "<friendly-console>", symbol: str = "single") -> bool: ...

    def runcode(self, code: types.CodeType) -> None: ...

    def showsyntaxerror(self, filename: Optional[str] = None) -> None: ...

    def showtraceback(self) -> None: ...


def start_console(local_vars: Optional[Mapping[str, Any]] = None, formatter: Union[str, Formatter] = "repl", include: InclusionChoice = "friendly_tb", lang: str = "en", banner: Optional[str] = None, displayhook: Optional[Callable[[object], Any]] = None, ipython_prompt: bool = True) -> None: ...
